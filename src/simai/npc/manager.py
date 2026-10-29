from dataclasses import dataclass
from typing import Protocol

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.actions.catalog import ActionDef, actions_for_location
from simai.actions.enums import ActionKind
from simai.actions.intent import choose_intent
from simai.actions.reachability import (
    available_moves,
    filter_moves_by_affordability,
)
from simai.actions.utility import (
    filter_by_affordability,
    filter_by_need_threshold,
    rng_for_decision,
)
from simai.economy.market import buy as market_buy
from simai.economy.market import filter_by_stock
from simai.economy.models import ShopItem
from simai.economy.service import job_of
from simai.economy.work import (
    WorkState,
    can_work,
    should_prioritize_home,
    should_prioritize_work,
    tick_in_day,
    work_state_for,
)
from simai.mood.moodlets import apply_moodlet, moodlets_for_action
from simai.needs.enums import NeedKind
from simai.needs.service import apply_effect, needs_of_many
from simai.relationships.service import boost_social_relationship
from simai.sim.reports import TickDecision
from simai.skills.service import skill_for_job_title, train_skill
from simai.world.enums import LocationKind
from simai.world.models import Character, Location
from simai.world.move import move_character


@dataclass
class NPCState:
    character_id: int
    key: str
    location_id: int
    home_location_id: int | None
    traits: list[str]
    balance: float
    needs: dict[NeedKind, float]
    is_player: bool


class NPCManagerLike(Protocol):
    def load(self, session: Session, *, include_player: bool) -> list[NPCState]: ...

    def update_all(
        self,
        session: Session,
        states: list[NPCState],
        *,
        tick_index: int,
        master_seed: int,
    ) -> list[TickDecision]: ...


def _all_actions_by_kind() -> dict[LocationKind, list[ActionDef]]:
    return {kind: actions_for_location(kind) for kind in LocationKind}


def _offers_by_key(session: Session) -> dict[tuple[str, ActionKind], int]:
    """Mappa `(location_key, action_kind) -> stock` in una query.

    Una sola query per tick, non una per NPC. Passata a
    `available_moves` per escludere location con stock esaurito.
    """
    items = session.scalars(select(ShopItem)).all()
    return {(item.location_key, item.action_kind): item.stock for item in items}


class NPCManager:
    """Astrazione sopra il loop di decisione del tick.

    In 1.5.0 il comportamento è identico a quello del loop inline
    precedente. Nessuna feature nuova. Il valore è architetturale:
    esiste un posto dove la FASE 3 può agganciarsi senza riscrivere
    `tick.py` ogni volta.

    `NPCState` è in-memory, ricostruito da DB a ogni `load()`. Non è
    persistito. `tick_one`/`update_all` mantengono `state` coerente
    con il DB per i campi che modificano: `location_id`, `balance`,
    `needs[satisfies]`.
    """

    def load(self, session: Session, *, include_player: bool) -> list[NPCState]:
        q = select(Character).order_by(Character.id)
        if not include_player:
            q = q.where(Character.is_player.is_(False))
        characters = session.scalars(q).all()

        character_ids = [c.id for c in characters]
        needs_by_id = needs_of_many(session, character_ids)

        states: list[NPCState] = []
        for char in characters:
            states.append(
                NPCState(
                    character_id=char.id,
                    key=char.key,
                    location_id=char.location_id,
                    home_location_id=char.home_location_id,
                    traits=list(char.traits),
                    balance=float(char.balance),
                    needs=needs_by_id.get(char.id, {}),
                    is_player=char.is_player,
                )
            )
        return states

    def update_all(
        self,
        session: Session,
        states: list[NPCState],
        *,
        tick_index: int,
        master_seed: int,
    ) -> list[TickDecision]:
        ordered = sorted(states, key=lambda s: s.character_id)
        offers_by_key = _offers_by_key(session)
        decisions: list[TickDecision] = []
        for state in ordered:
            decision = self._tick_one(
                session,
                state,
                tick_index=tick_index,
                master_seed=master_seed,
                offers_by_key=offers_by_key,
            )
            decisions.append(decision)
        return decisions

    def _tick_one(
        self,
        session: Session,
        state: NPCState,
        *,
        tick_index: int,
        master_seed: int,
        offers_by_key: dict[tuple[str, ActionKind], int] | None = None,
    ) -> TickDecision:
        char = session.get(Character, state.character_id)
        if char is None:
            raise RuntimeError(f"Character id={state.character_id} non trovato in DB")
        loc = session.get(Location, state.location_id)
        if loc is None:
            raise RuntimeError(f"Character {state.key} has invalid location_id={state.location_id}")

        traits = list(state.traits)
        needs = dict(state.needs)
        catalog_by_kind = _all_actions_by_kind()

        actions = actions_for_location(loc.kind)
        local_actions = filter_by_need_threshold(actions, needs)
        local_actions = filter_by_affordability(local_actions, state.balance)
        local_actions = filter_by_stock(session, local_actions, loc.key)
        local_satisfies = {a.satisfies for a in local_actions}

        raw_moves = available_moves(
            session,
            current_location_id=loc.id,
            needs=needs,
            offers_by_key=offers_by_key,
        )
        raw_moves = [m for m in raw_moves if m.satisfies not in local_satisfies]
        moves = filter_moves_by_affordability(raw_moves, state.balance, catalog_by_kind)

        t_in_day = tick_in_day(tick_index)
        job = job_of(session, state.character_id)
        hunger = needs.get(NeedKind.HUNGER, 100.0)
        age_years = char.age_years

        # Divieto lavoro pediatrico (non-STUDENTE): job sospeso.
        # `char` è già stato caricato sopra, `age_years` è disponibile.
        if not can_work(job, age_years):
            job = None
        # 0.1150: training durante WORKING (a prescindere dall'azione).
        if (
            job is not None
            and loc.key == job.location_key
            and work_state_for(job, t_in_day) == WorkState.WORKING
        ):
            train_skill(
                session,
                state.character_id,
                skill_for_job_title(job.title.value),
                0.001,
            )

        if should_prioritize_work(job, t_in_day, hunger, age_years=age_years):
            assert job is not None
            if loc.key != job.location_key:
                result = move_character(session, state.key, job.location_key)
                if not result.success:
                    raise RuntimeError(f"Move lavoro fallito per {state.key}: {result.error}")
                self._sync_location(session, state)
                return TickDecision(
                    character_id=state.character_id,
                    character_key=state.key,
                    location_key=loc.key,
                    action=None,
                    satisfied=None,
                    value_before=None,
                    value_after=None,
                    moved_from=result.from_location_key,
                    moved_to=result.to_location_key,
                )
            moves = []

        if job is not None and not should_prioritize_work(
            job, t_in_day, hunger, age_years=age_years
        ):
            home_loc = (
                session.get(Location, state.home_location_id)
                if state.home_location_id is not None
                else None
            )
            home_key = home_loc.key if home_loc else None
            intimacy = needs.get(NeedKind.INTIMACY, 100.0)
            fun = needs.get(NeedKind.FUN, 100.0)
            if should_prioritize_home(
                job,
                t_in_day,
                home_key,
                loc.key,
                intimacy,
                fun,
            ):
                assert home_loc is not None
                result = move_character(session, state.key, home_loc.key)
                if not result.success:
                    raise RuntimeError(f"Move casa fallito per {state.key}: {result.error}")
                self._sync_location(session, state)
                return TickDecision(
                    character_id=state.character_id,
                    character_key=state.key,
                    location_key=loc.key,
                    action=None,
                    satisfied=None,
                    value_before=None,
                    value_after=None,
                    moved_from=result.from_location_key,
                    moved_to=result.to_location_key,
                )

        rng = rng_for_decision(master_seed, state.character_id, tick_index)
        intent = choose_intent(needs, local_actions, moves, rng, traits)

        if intent.move is not None:
            result = move_character(session, state.key, intent.move.target_location_key)
            if not result.success:
                raise RuntimeError(f"Move fallito per {state.key}: {result.error}")
            self._sync_location(session, state)
            return TickDecision(
                character_id=state.character_id,
                character_key=state.key,
                location_key=loc.key,
                action=None,
                satisfied=None,
                value_before=None,
                value_after=None,
                moved_from=result.from_location_key,
                moved_to=result.to_location_key,
            )

        if intent.action is None:
            logger.debug(
                f"Nessuna azione per {state.key} in {loc.key}: nessuna azione o move disponibile."
            )
            return TickDecision(
                character_id=state.character_id,
                character_key=state.key,
                location_key=loc.key,
                action=None,
                satisfied=None,
                value_before=None,
                value_after=None,
            )

        action = intent.action
        before = needs[action.satisfies]
        after = apply_effect(session, state.character_id, action)
        state.needs[action.satisfies] = after

        cost_paid = 0.0
        if action.cost > 0:
            purchase = market_buy(
                session,
                char,
                loc.key,
                action,
                tick_index=tick_index,
            )
            if not purchase.success:
                logger.warning(
                    f"Acquisto fallito per {state.key} "
                    f"({action.kind.value} @ {loc.key}): {purchase.error}"
                )
                return TickDecision(
                    character_id=state.character_id,
                    character_key=state.key,
                    location_key=loc.key,
                    action=None,
                    satisfied=None,
                    value_before=None,
                    value_after=None,
                )
            cost_paid = purchase.price_paid
            state.balance = float(char.balance)

        rel_after = boost_social_relationship(session, state.character_id, action)
        moodlet_kind = moodlets_for_action(action.kind)
        if moodlet_kind is not None:
            apply_moodlet(session, state.character_id, moodlet_kind, tick_index)

        return TickDecision(
            character_id=state.character_id,
            character_key=state.key,
            location_key=loc.key,
            action=action.kind,
            satisfied=action.satisfies,
            value_before=before,
            value_after=after,
            relationship_strength_after=rel_after,
            cost_paid=cost_paid,
        )

    @staticmethod
    def _sync_location(session: Session, state: NPCState) -> None:
        char = session.get(Character, state.character_id)
        if char is not None:
            state.location_id = char.location_id
