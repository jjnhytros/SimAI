"""Route: NPC (lista, dettaglio, albero)."""

from __future__ import annotations

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from simai.economy import MarketService
from simai.economy.models import ShopItem
from simai.npc.addictions import AddictionService
from simai.npc.background import BackgroundService
from simai.npc.desire import DesireService
from simai.npc.identity import IdentityService
from simai.npc.memory.service import MemoryService
from simai.npc.models import Character
from simai.npc.mood import MoodState
from simai.npc.needs.needs import Needs
from simai.npc.personality import PersonalityService
from simai.npc.reflection import CrisisService, ReflectionService
from simai.npc.relationships.family_tree import FamilyTreeService
from simai.npc.relationships.models import Relationship
from simai.npc.skills.service import SkillService
from simai.npc.social_awareness import SocialAwarenessService
from simai.ui.app import templates
from simai.ui.deps import get_db
from simai.utils import coerce_int

router = APIRouter()


@router.get("/npcs", response_class=HTMLResponse)
def npcs_list(
    request: Request,
    session: Session = Depends(get_db),
    alive_only: bool = Query(default=False),
    limit: int = Query(default=200, ge=1, le=1000),
) -> HTMLResponse:
    """Lista NPC con filtri base."""
    stmt = select(Character).order_by(Character.id).limit(limit)
    if alive_only:
        stmt = stmt.where(Character.is_alive.is_(True))
    chars = list(session.scalars(stmt))

    max_tick = int(session.scalar(select(func.max(Character.last_ai_tick))) or 0)

    rows: list[dict[str, object]] = []
    for c in chars:
        skills = SkillService.all_skills(session, c.id)
        best_skill = max(skills, key=lambda s: s.level, default=None)
        rows.append(
            {
                "id": c.id,
                "name": c.full_name,
                "sex": c.sex,
                "alive": c.is_alive,
                "birth_iso": c.birth_iso,
                "best_skill": best_skill.skill_type if best_skill else "—",
                "best_level": best_skill.level if best_skill else 0,
                "balance": int(c.athel_balance),
            }
        )

    return templates.TemplateResponse(
        request,
        "npcs_list.html",
        {
            "npcs": rows,
            "alive_only": alive_only,
            "limit": limit,
            "current_tick": max_tick,
        },
    )


@router.get("/npcs/{character_id}", response_class=HTMLResponse)
def npc_detail(
    request: Request,
    character_id: int,
    session: Session = Depends(get_db),
) -> HTMLResponse:
    """Dettaglio NPC."""
    c = session.get(Character, character_id)
    if c is None:
        raise HTTPException(status_code=404, detail=f"NPC {character_id} non trovato")

    # Needs / Mood
    needs = Needs.from_dict(c.needs_json or {})
    mood = MoodState.from_dict(c.mood_json or {})

    # Skills
    skills = SkillService.all_skills(session, c.id)

    # Personality / Values
    PersonalityService.initialize(c)
    personality = PersonalityService.summary(c)

    # Identity
    identity = IdentityService.get_profile(c)

    # Desire / Crisis
    desire = DesireService.get_state(c)
    crisis = CrisisService.get_status(c)

    # Addictions
    addictions = AddictionService.all_of(session, c.id)

    # Background
    background = BackgroundService.all_of(session, c.id)

    # Reflections (ultime 10)
    reflections = ReflectionService.recent_entries(session, c.id, limit=10)

    # Memories (ultime 10)
    memories = MemoryService.recall(session, c.id, limit=10)

    # Relationships (uscenti)
    rels_out = list(session.scalars(select(Relationship).where(Relationship.from_id == c.id)))
    rel_rows: list[dict[str, object]] = []
    for rel in rels_out:
        other = session.get(Character, rel.to_id)
        if other is None:
            continue
        rel_rows.append(
            {
                "kind": rel.kind,
                "other_id": other.id,
                "other_name": other.full_name,
                "strength": rel.strength,
            }
        )

    # Family
    parents = FamilyTreeService.parents_of(session, c.id)
    children = FamilyTreeService.children_of(session, c.id)
    siblings = FamilyTreeService.siblings_of(session, c.id)

    # Knowledge (cosa sa degli altri)
    known_count = 0
    for other in session.scalars(select(Character).where(Character.id != c.id)):
        known_count += len(SocialAwarenessService.known_traits(c, other.id))

    return templates.TemplateResponse(
        request,
        "npc_detail.html",
        {
            "c": c,
            "needs": needs,
            "mood": mood,
            "skills": skills,
            "personality": personality,
            "identity": identity,
            "desire": desire,
            "crisis": crisis,
            "addictions": addictions,
            "background": background,
            "reflections": reflections,
            "memories": memories,
            "relationships": rel_rows,
            "parents": parents,
            "children": children,
            "siblings": siblings,
            "known_count": known_count,
        },
    )


@router.get("/npcs/{character_id}/tree", response_class=HTMLResponse)
def npc_tree(
    request: Request,
    character_id: int,
    session: Session = Depends(get_db),
) -> HTMLResponse:
    """Albero genealogico interattivo (D3)."""
    c = session.get(Character, character_id)
    if c is None:
        raise HTTPException(status_code=404, detail=f"NPC {character_id} non trovato")

    return templates.TemplateResponse(
        request,
        "npc_tree.html",
        {"c": c},
    )


@router.get("/api/npcs/{character_id}/recipes.json")
def api_npc_recipes(
    character_id: int,
    session: Session = Depends(get_db),
) -> JSONResponse:
    """Ritorna le ricette disponibili per un character con dettagli input."""
    from fastapi.responses import JSONResponse

    from simai.npc.crafting import CraftingService, all_recipes

    c = session.get(Character, character_id)
    if c is None:
        raise HTTPException(status_code=404, detail="Character non trovato")

    items = []
    for r in all_recipes():
        missing = CraftingService.missing_inputs(session, c, r)
        from simai.npc.skills.service import SkillService

        skill = SkillService.get_skill(session, c.id, r.required_skill)
        lvl = skill.level if skill else 0
        items.append(
            {
                "code": r.code,
                "output_type": r.output_type,
                "output_name": r.output_name,
                "required_skill": r.required_skill.value,
                "min_skill_level": r.min_skill_level,
                "current_skill_level": lvl,
                "skill_ok": lvl >= r.min_skill_level,
                "inputs": r.inputs,
                "missing": {k: {"have": h, "need": n} for k, (h, n) in missing.items()},
                "base_value": r.base_value,
                "description": r.description,
            }
        )
    return JSONResponse({"recipes": items})


@router.get("/api/npcs/{character_id}/inventory.json")
def api_npc_inventory(
    character_id: int,
    session: Session = Depends(get_db),
) -> JSONResponse:
    """Ritorna l'inventario di un NPC con qualità (se craftato)."""
    from fastapi.responses import JSONResponse

    from simai.world.models import GameObject

    c = session.get(Character, character_id)
    if c is None:
        raise HTTPException(status_code=404, detail="Character non trovato")

    from sqlalchemy import select as _sel

    objs = list(
        session.scalars(
            _sel(GameObject)
            .where(GameObject.owner_character_id == character_id)
            .order_by(GameObject.type, GameObject.id)
        )
    )
    items = []
    for o in objs:
        meta = o.metadata_json or {}
        items.append(
            {
                "id": o.id,
                "name": o.name,
                "type": o.type,
                "state": o.state,
                "condition": o.condition,
                "crafted": bool(meta.get("crafted")),
                "quality_label": str(meta.get("quality_label", "")),
                "quality_value": float(meta.get("quality_value", 0.0)),
            }
        )
    return JSONResponse({"character_id": character_id, "items": items})


# ---------------------------------------------------------------------------
# Sell (Chunk 4.8c)
# ---------------------------------------------------------------------------


@router.get("/api/items/{item_type}/buyers.json")
def api_item_buyers(
    item_type: str,
    session: Session = Depends(get_db),
) -> JSONResponse:
    """Ritorna i negozi che comprano `item_type` (con stock attuale)."""
    from simai.world.models import Location

    rows = list(session.scalars(select(ShopItem).where(ShopItem.item_type == item_type)))
    shops: list[dict[str, object]] = []
    for item in rows:
        loc = session.get(Location, item.location_id)
        if loc is None:
            continue
        shops.append(
            {
                "id": loc.id,
                "name": loc.name,
                "current_price": item.current_price,
                "stock": item.stock,
            }
        )
    return JSONResponse({"item_type": item_type, "shops": shops})


@router.post("/api/npcs/{character_id}/sell")
def api_sell_item(
    character_id: int,
    payload: dict[str, object] = Body(...),
    session: Session = Depends(get_db),
) -> JSONResponse:
    """Vende un oggetto dal inventario di un NPC a un negozio."""
    from simai.config.settings import get_settings
    from simai.core.anthalys_datetime import AnthalysDateTime
    from simai.world.models import GameObject, Location

    seller = session.get(Character, character_id)
    if seller is None:
        raise HTTPException(status_code=404, detail=f"Character {character_id} non trovato")

    try:
        object_id = coerce_int(payload["object_id"], name="object_id")
        shop_id = coerce_int(payload["shop_id"], name="shop_id")
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Campo mancante: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Payload non valido: {exc}") from exc

    obj = session.get(GameObject, object_id)
    if obj is None or obj.owner_character_id != character_id:
        raise HTTPException(status_code=404, detail="Oggetto non trovato o non tuo")
    shop = session.get(Location, shop_id)
    if shop is None:
        raise HTTPException(status_code=404, detail=f"Shop {shop_id} non trovato")

    settings = get_settings()
    start = AnthalysDateTime(settings.starting_year, settings.starting_month, settings.starting_day)

    result = MarketService.sell(session, seller=seller, shop=shop, obj=obj, current_dt=start)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.reason)
    session.commit()
    return JSONResponse(
        {
            "ok": True,
            "price_received": result.price_received,
            "base_price": result.base_price,
            "quality_label": result.quality_label,
        }
    )
