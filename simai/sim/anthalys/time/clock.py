"""AnthalysClock — facade di alto livello su TimeManager + dominio Anthalys."""

from __future__ import annotations

from simai.core.anthalys_datetime import AnthalysDateTime
from simai.core.time_manager import TimeManager
from simai.sim.anthalys.time.astro import AstroEvent, AstroEventsEngine
from simai.sim.anthalys.time.holidays import Holiday, HolidayRegistry
from simai.sim.anthalys.time.moons import MoonCycles, MoonPhase
from simai.sim.anthalys.time.seasons import SeasonInfo, season_info


class AnthalysClock:
    """Wrapper di `TimeManager` arricchito con dati Anthalys.

    Non è un singleton. Costruire una istanza per simulazione, passando
    (opzionalmente) registry, cicli lunari ed engine astro custom.

    Esempio:
        tm = TimeManager(start=D(5775, 1, 1), tick_minutes=5)
        clock = AnthalysClock(tm)
        clock.advance_ticks(400)
        print(clock.current_holidays)
    """

    def __init__(
        self,
        time_manager: TimeManager,
        *,
        holidays: HolidayRegistry | None = None,
        moons: MoonCycles | None = None,
        master_seed: int = 0,
    ) -> None:
        self._tm = time_manager
        self._holidays = holidays if holidays is not None else HolidayRegistry.default()
        self._moons = moons if moons is not None else MoonCycles.default()
        self._astro = AstroEventsEngine(moons=self._moons, master_seed=master_seed)

    # ------------------------------------------------------------------
    # Delegates
    # ------------------------------------------------------------------

    @property
    def time_manager(self) -> TimeManager:
        return self._tm

    @property
    def current(self) -> AnthalysDateTime:
        return self._tm.current

    @property
    def current_phase(self):  # type: ignore[no-untyped-def]
        return self._tm.current_phase

    @property
    def current_season(self):  # type: ignore[no-untyped-def]
        return self._tm.current_season

    def advance_tick(self) -> None:
        self._tm.advance_tick()

    def advance_ticks(self, n: int) -> None:
        self._tm.advance_ticks(n)

    # ------------------------------------------------------------------
    # Anthalys-specific
    # ------------------------------------------------------------------

    @property
    def holidays(self) -> HolidayRegistry:
        return self._holidays

    @property
    def moons(self) -> MoonCycles:
        return self._moons

    @property
    def astro(self) -> AstroEventsEngine:
        return self._astro

    def current_holidays(self) -> list[Holiday]:
        """Festività che cadono esattamente al tempo corrente."""
        return self._holidays.on_date(self.current, self._moons)

    def current_moon_phases(self) -> dict[str, MoonPhase]:
        """Fase di ogni luna al tempo corrente."""
        return self._moons.all_phases(self.current)

    def current_season_info(self) -> SeasonInfo:
        """Metadati estesi della stagione corrente."""
        return season_info(self.current)

    def next_holiday(self) -> tuple[AnthalysDateTime, list[Holiday]] | None:
        """Prossima festività futura."""
        return self._holidays.next_after(self.current, self._moons)

    def next_astro_events(self, *, horizon_days: int = 2000) -> list[AstroEvent]:
        """Prossimi eventi astronomici entro `horizon_days` giorni."""
        return self._astro.next_events(self.current, horizon_days=horizon_days)


__all__ = ["AnthalysClock"]
