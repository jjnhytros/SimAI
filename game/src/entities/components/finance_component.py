# game/src/entities/components/finance_component.py
import logging
import random # Per un valore iniziale casuale se non fornito
from typing import Dict, Any, Optional, List, Tuple, TYPE_CHECKING

# Importa dal package 'game'
from game import config # Per valori di default come NPC_INITIAL_MONEY_MIN/MAX

if TYPE_CHECKING:
    from game.src.entities.character import Character # Per il type hint di character_owner
    from game.src.modules.game_state_module import GameState # Per accedere al tempo di gioco

logger = logging.getLogger(__name__)
DEBUG_FINANCE = getattr(config, 'DEBUG_AI_ACTIVE', False) # Puoi usare un flag di debug specifico

class FinanceComponent:
    def __init__(self, character_owner: 'Character', initial_money: Optional[float] = None):
        """
        Inizializza il componente finanziario.

        Args:
            character_owner (Character): Il personaggio a cui questo componente appartiene.
            initial_money (Optional[float]): Il denaro iniziale. 
                                             Se None, viene generato casualmente.
        """
        self.owner: 'Character' = character_owner # Riferimento al proprietario
        self.owner_name: str = character_owner.name if character_owner else "NPC Sconosciuto"

        if initial_money is None:
            self.balance: float = float(random.uniform(
                getattr(config, 'NPC_INITIAL_MONEY_MIN', 500),
                getattr(config, 'NPC_INITIAL_MONEY_MAX', 2000)
            ))
        else:
            self.balance: float = float(initial_money)
        
        # Lista di tuple: (descrizione, importo, timestamp_gioco_ore_totali)
        self.transaction_history: List[Tuple[str, float, float]] = [] 
        
        # Attributi futuri potrebbero includere:
        # self.income_sources: List[IncomeSource] = []
        # self.recurring_expenses: List[RecurringExpense] = []
        # self.assets: Dict[str, float] = {} # Es. {"casa": 150000}
        # self.debts: Dict[str, float] = {}  # Es. {"mutuo_casa": 120000}
        
        if DEBUG_FINANCE:
            logger.debug(f"FinanceComponent per {self.owner_name} inizializzato. Saldo: ${self.balance:.2f}")

    def _get_current_game_time(self) -> float:
        """Helper per ottenere il tempo di gioco corrente in ore totali trascorse."""
        if self.owner and hasattr(self.owner, 'game_state_ref') and self.owner.game_state_ref:
            if hasattr(self.owner.game_state_ref, 'current_game_total_sim_hours_elapsed'):
                return self.owner.game_state_ref.current_game_total_sim_hours_elapsed
            elif hasattr(self.owner.game_state_ref, 'game_time_handler') and self.owner.game_state_ref.game_time_handler:
                # Fallback se current_game_total_sim_hours_elapsed non è direttamente su game_state
                # Questo presuppone che GameTimeManager abbia un modo per dare i secondi totali
                # e che abbiamo bisogno di ore. Per ora, usiamo la variabile diretta da game_state
                # se popolata dal GameTimeManager.
                # Per semplicità, assumiamo che current_game_total_sim_hours_elapsed sia l'attributo corretto.
                pass # Non fare nulla qui, il primo check è sufficiente
        return 0.0 # Fallback se il tempo non può essere recuperato


    def add_money(self, amount: float, description: str = "Reddito generico") -> bool:
        """Aggiunge denaro al saldo."""
        if amount <= 0:
            logger.warning(f"Finance ({self.owner_name}): Tentativo di aggiungere un importo non positivo: ${amount:.2f} ({description})")
            return False
        
        self.balance += amount
        current_game_time_hours = self._get_current_game_time()
        self.transaction_history.append((description, amount, current_game_time_hours))
        
        max_history = getattr(config, 'MAX_TRANSACTION_HISTORY', 50)
        if len(self.transaction_history) > max_history:
            self.transaction_history.pop(0) # Rimuovi la transazione più vecchia
            
        if DEBUG_FINANCE:
            logger.debug(f"Finance ({self.owner_name}): Aggiunti ${amount:.2f} ({description}). Nuovo saldo: ${self.balance:.2f}")
        return True

    def spend_money(self, amount: float, description: str = "Spesa generica") -> bool:
        """Sottrae denaro dal saldo se disponibile."""
        if amount <= 0:
            logger.warning(f"Finance ({self.owner_name}): Tentativo di spendere un importo non positivo: ${amount:.2f} ({description})")
            return False
            
        if self.balance >= amount:
            self.balance -= amount
            current_game_time_hours = self._get_current_game_time()
            self.transaction_history.append((description, -amount, current_game_time_hours))

            max_history = getattr(config, 'MAX_TRANSACTION_HISTORY', 50)
            if len(self.transaction_history) > max_history:
                self.transaction_history.pop(0)

            if DEBUG_FINANCE:
                logger.debug(f"Finance ({self.owner_name}): Spesi ${amount:.2f} ({description}). Nuovo saldo: ${self.balance:.2f}")
            return True
        else:
            if DEBUG_FINANCE:
                logger.warning(f"Finance ({self.owner_name}): Tentativo di spendere ${amount:.2f} ({description}) fallito. Saldo insufficiente: ${self.balance:.2f}")
            return False

    def get_balance(self) -> float:
        """Restituisce il saldo corrente."""
        return self.balance

    def update(self, game_hours_advanced: float, game_state_ref: 'GameState'):
        """
        Aggiorna lo stato finanziario (es. interessi, stipendi, bollette).
        Chiamata dal Character.update() o da un gestore finanziario globale.

        Args:
            game_hours_advanced (float): Le ore di gioco trascorse in questo tick.
            game_state_ref (GameState): Riferimento allo stato del gioco.
        """
        # Esempio di logica futura:
        # Stipendio (se l'NPC ha un lavoro e questo componente interagisce con CareerComponent)
        # if self.owner and hasattr(self.owner, 'career') and self.owner.career and self.owner.career.is_working_now:
        #     hourly_wage = self.owner.career.get_hourly_wage()
        #     earned_this_tick = hourly_wage * game_hours_advanced
        #     if earned_this_tick > 0:
        #         self.add_money(earned_this_tick, f"Stipendio da {self.owner.career.job_title}")

        # Spese ricorrenti (es. affitto, bollette)
        # Questo potrebbe essere gestito da un sistema a eventi o giornaliero/mensile
        # if game_state_ref.game_time_handler.is_new_day() and game_state_ref.game_time_handler.day == 1: # Inizio del mese
        #     rent_amount = getattr(config, 'MONTHLY_RENT_AMOUNT', 300)
        #     self.spend_money(rent_amount, "Affitto mensile")
        
        pass # Per ora, nessuna logica di update automatico implementata

    def to_dict(self) -> Dict[str, Any]:
        """Serializza lo stato finanziario."""
        # La cronologia delle transazioni potrebbe diventare molto grande.
        # Per il salvataggio, potremmo volerla omettere o salvare solo le ultime N.
        # Per ora, la escludiamo.
        return {
            "balance": self.balance,
            # "transaction_history_tuples": self.transaction_history # Se si decide di salvarla
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]], character_owner: 'Character') -> 'FinanceComponent':
        """Crea un'istanza di FinanceComponent da dati serializzati."""
        initial_balance = None
        if data and "balance" in data:
            initial_balance = float(data["balance"])
        # Se initial_balance è None (perché data è None o "balance" non c'è),
        # il costruttore di FinanceComponent userà i valori casuali di default.
        
        instance = cls(character_owner=character_owner, initial_money=initial_balance)
        
        # Se si salvasse e caricasse la transaction_history:
        # if data and "transaction_history_tuples" in data:
        #     instance.transaction_history = [tuple(t) for t in data["transaction_history_tuples"]]
            
        if DEBUG_FINANCE and data: # Log solo se c'erano dati da caricare
            logger.debug(f"FinanceComponent per {character_owner.name} caricato. Saldo: ${instance.balance:.2f}")
        return instance