# core/modules/needs/need_base.py
"""
Definizione della classe base astratta per tutti i tipi di Bisogno (Need) degli NPC.
Riferimento TODO: V.a.i
"""
from abc import ABC, abstractmethod
from typing import Optional

from core.enums import NeedType # Assicurati che NeedType sia definito e importabile
from core import settings     # Per i valori di default, min/max, soglie

class BaseNeed(ABC):
    def __init__(self, 
                 need_type: NeedType, 
                 initial_value: Optional[float] = None,
                 decay_rate_per_hour: float = 0.0): # Il tasso di decadimento specifico
        """
        Costruttore per la BaseNeed.

        Args:
            need_type (NeedType): Il tipo di bisogno (dall'Enum NeedType).
            initial_value (Optional[float]): Valore iniziale del bisogno. 
                                             Se None, verrà randomizzato.
            decay_rate_per_hour (float): Tasso di decadimento orario (negativo per decadere).
        """
        self.need_type: NeedType = need_type
        self.value: float
        
        # Costanti del bisogno (potrebbero essere sovrascritte da sottoclassi se necessario)
        self._min_value: float = settings.NEED_MIN_VALUE
        self._max_value: float = settings.NEED_MAX_VALUE
        self._critical_threshold: float = settings.NEED_CRITICAL_THRESHOLD
        self._low_threshold: float = settings.NEED_LOW_THRESHOLD
        
        # Il tasso di decadimento è specifico per ogni tipo di bisogno concreto
        self.decay_rate_per_hour: float = decay_rate_per_hour

        if initial_value is None:
            import random
            self.value = random.uniform(settings.NEED_DEFAULT_START_MIN, settings.NEED_DEFAULT_START_MAX)
        else:
            self.value = initial_value
        
        # Applica subito il clamping al valore iniziale
        self._clamp_value()

        # Non è necessario un print di DEBUG qui, Character lo farà quando inizializza i suoi bisogni.

    def _clamp_value(self):
        """Mantiene il valore del bisogno entro i limiti min e max."""
        self.value = max(self._min_value, min(self._max_value, self.value))

    def get_value(self) -> float:
        """Restituisce il valore corrente del bisogno."""
        return self.value

    def get_type(self) -> NeedType:
        """Restituisce il tipo di bisogno (membro dell'Enum NeedType)."""
        return self.need_type

    def display_name(self) -> str:
        """Restituisce il nome visualizzabile del bisogno."""
        return self.need_type.display_name_it() # Usa il metodo dell'Enum

    def is_critical(self) -> bool:
        """Indica se il bisogno è a un livello critico."""
        return self.value <= self._critical_threshold

    def is_low(self) -> bool:
        """Indica se il bisogno è a un livello basso (ma non ancora critico)."""
        return self.value <= self._low_threshold and self.value > self._critical_threshold

    def change_value(self, amount: float, is_decay_event: bool = False, character_name_for_log: Optional[str] = None) -> float:
        """
        Modifica il valore del bisogno dell'ammontare specificato e applica il clamping.
        Restituisce la variazione effettiva dopo il clamping.
        'character_name_for_log' è usato per rendere i log più specifici.
        """
        old_value = self.value
        self.value += amount
        self._clamp_value()
        actual_change = self.value - old_value

        if settings.DEBUG_MODE and abs(actual_change) > 0.00001: # Logga solo se c'è stato un cambiamento reale
            log_char_name = character_name_for_log if character_name_for_log else "NPC"
            
            if is_decay_event:
                # Per il decadimento, non logghiamo più ad ogni singolo cambiamento per ridurre lo spam.
                # Gli alert per soglie basse/critiche (sotto) sono più importanti.
                # Se si vuole un log di decadimento, si può aggiungere una condizione di frequenza
                # (es. ogni tot tick o se il cambiamento supera una certa soglia maggiore).
                # Esempio (attualmente commentato):
                # if abs(actual_change) > 0.5: # Logga solo se il decadimento in un colpo è significativo
                #     print(f"    [Need {self.need_type.name} - {log_char_name}] DECAY: {old_value:.2f} -> {self.value:.2f} (Delta: {actual_change:.3f})")
                pass # Il decadimento avviene, ma il log dettagliato per ogni tick è rimosso.
            else: # Logga sempre soddisfazioni o altri cambiamenti diretti non di decadimento
                print(f"    [Need {self.need_type.name} - {log_char_name}] CHANGE: {old_value:.2f} -> {self.value:.2f} (Delta: {actual_change:.3f})")

            # Manteniamo i log per le soglie critiche/basse quando vengono superate (solo per riduzioni)
            if actual_change < 0: 
                if self.is_critical() and old_value > self._critical_threshold:
                    print(f"      L> [ALERT!!! - {log_char_name}] {self.display_name()} è CRITICO: {self.value:.1f}")
                elif self.is_low() and old_value > self._low_threshold: # Logga quando *diventa* basso
                    print(f"      L> [ALERT! - {log_char_name}] {self.display_name()} è BASSO: {self.value:.1f}")
        return actual_change


    def decay(self, fraction_of_hour_elapsed: float, character_name_for_log: Optional[str] = None):
        """
        Applica il decadimento al bisogno in base al tempo trascorso.
        Le sottoclassi concrete imposteranno self.decay_rate_per_hour.
        """
        if self.decay_rate_per_hour == 0.0: # Nessun decadimento passivo per questo bisogno
            return

        decay_amount_for_period = self.decay_rate_per_hour * fraction_of_hour_elapsed
        
        if abs(decay_amount_for_period) > 0.000001:
            self.change_value(decay_amount_for_period, is_decay_event=True, character_name_for_log=character_name_for_log)
        # else:
            # Se si vuole loggare anche quando il decadimento è troppo piccolo per essere applicato:
            # if settings.DEBUG_MODE and character_name_for_log:
            #     print(f"    [Need {self.need_type.name} - {character_name_for_log}] Decadimento per periodo ({decay_amount_for_period:.5f}) troppo piccolo, nessun cambiamento.")

    # Potrebbe avere un metodo astratto se alcuni bisogni hanno logiche di decadimento uniche
    # @abstractmethod
    # def custom_decay_logic(self, time_manager: TimeManager):
    #     pass