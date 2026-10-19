from sqlalchemy.orm import Session

from simai.sim.models import SimState

SINGLETON_ID = 1


def get_state(session: Session) -> SimState:
    """Ritorna lo stato di simulazione, creandolo se mancante."""
    state = session.get(SimState, SINGLETON_ID)
    if state is None:
        state = SimState(id=SINGLETON_ID, tick_index=0, master_seed=42)
        session.add(state)
        session.flush()
    return state


def reset_state(session: Session, master_seed: int) -> SimState:
    state = get_state(session)
    state.tick_index = 0
    state.master_seed = master_seed
    session.flush()
    return state
