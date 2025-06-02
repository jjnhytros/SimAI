# core/modules/needs/need_base.py
"""
Definizione della classe base astratta per tutti i Bisogni (Needs) degli NPC.
Riferimento TODO: IV.1.a, IV.1.b, IV.1.c
"""
from abc import ABC, abstractmethod
from typing import Optional
import random # Assicurati che random sia importato

from core.enums import NeedType
from core import settings

class BaseNeed(ABC):
    """
    Classe base per i bisogni degli NPC.
    Gestisce il valore del bisogno, il suo decadimento e i limiti.
    """
    def __init__(self,
                p_need_type: NeedType, 
                initial_value: Optional[float] = None,
                decay_rate_per_hour: float = 0.0,
                min_value: float = settings.NEED_MIN_VALUE,
                max_value: float = settings.NEED_MAX_VALUE
                ):
        self.need_type: NeedType = p_need_type # Assegna il tipo di bisogno
        self.decay_rate_per_hour: float = decay_rate_per_hour
        self._min_value: float = min_value
        self._max_value: float = max_value
        
        # Attributo per il valore numerico del bisogno.
        # Il type hint da solo non inizializza.
        self.value: float 

        # --- MODIFICA: Assicura l'inizializzazione di self.value (float) ---
        if initial_value is not None:
            self.value = initial_value
        else:
            # Inizializzazione di default se nessun valore specifico è fornito.
            self.value = random.uniform(
                getattr(settings, "NEED_DEFAULT_START_MIN", 50.0),
                getattr(settings, "NEED_DEFAULT_START_MAX", 80.0)
            )
        # --- FINE MODIFICA ---
            
        self._clamp_value() # Chiamato alla fine per assicurare che il valore sia nei limiti

    def _clamp_value(self):
        """Assicura che il valore del bisogno rimanga tra min_value e max_value."""
        # Ora self.value dovrebbe essere sempre un float prima di questa chiamata.
        self.value = max(self._min_value, min(self._max_value, self.value))

    def get_value(self) -> float:
        """Restituisce il valore corrente del bisogno."""
        return self.value

    def set_value(self, new_value: float, character_name_for_log: Optional[str] = None):
        """
        Imposta il valore del bisogno a un valore specifico, applicando il clamping.
        Opzionalmente logga il cambiamento se DEBUG_MODE è attivo e il nome del personaggio è fornito.
        """
        old_value = self.value
        self.value = new_value
        self._clamp_value()
        if settings.DEBUG_MODE and character_name_for_log and old_value != self.value:
            # Logga solo se c'è un cambiamento effettivo e abbiamo un contesto
            print(f"    [Need Set - {character_name_for_log}] Bisogno '{self.need_type.name}' impostato a {self.value:.1f} (da {old_value:.1f})")


    def change_value(self, amount: float, is_decay_event: bool = False, character_name_for_log: Optional[str] = None):
        """
        Modifica il valore del bisogno dell'ammontare specificato.
        Se is_decay_event è True, il cambiamento è considerato un decadimento naturale.
        Logga il cambiamento se in DEBUG_MODE, il nome del personaggio è fornito e il cambiamento non è un decadimento (o se è un decadimento significativo).
        """
        old_value = self.value
        self.value += amount
        self._clamp_value()

        # Logica di logging migliorata per ridurre la verbosità
        log_this_change = False
        if settings.DEBUG_MODE and character_name_for_log and old_value != self.value:
            if not is_decay_event: # Logga sempre i guadagni o le perdite indotte
                log_this_change = True
            else: # Per i decadimenti, logga solo se supera soglie o è significativo
                is_now_low = self.value <= settings.NEED_LOW_THRESHOLD and old_value > settings.NEED_LOW_THRESHOLD
                is_now_critical = self.value <= settings.NEED_CRITICAL_THRESHOLD and old_value > settings.NEED_CRITICAL_THRESHOLD
                if is_now_low or is_now_critical:
                    log_this_change = True
        
        if log_this_change:
            decay_tag = " (Decay)" if is_decay_event else ""
            critical_status = ""
            if self.value <= settings.NEED_CRITICAL_THRESHOLD: critical_status = " [!!! CRITICO !!!]"
            elif self.value <= settings.NEED_LOW_THRESHOLD: critical_status = " [! Basso !]"
            
            print(f"    [Need Change - {character_name_for_log}] Bisogno '{self.need_type.name}'{decay_tag}: {old_value:.1f} -> {self.value:.1f} (Δ {amount:.1f}){critical_status}")


    def decay(self, fraction_of_hour_elapsed: float, character_name_for_log: Optional[str] = None):
        """
        Applica il decadimento al bisogno in base alla frazione di ora trascorsa.
        Questo metodo ora utilizza self.decay_rate_per_hour che è negativo per il decadimento.
        """
        if self.decay_rate_per_hour == 0: # Nessun decadimento per questo bisogno
            return
        
        # self.decay_rate_per_hour è già il valore per ora (es. -5.0 per ENERGIA)
        # quindi moltiplichiamo direttamente per la frazione di ora
        amount_to_decay = self.decay_rate_per_hour * fraction_of_hour_elapsed
        
        if amount_to_decay != 0: # Applica solo se c'è un cambiamento
            self.change_value(amount_to_decay, is_decay_event=True, character_name_for_log=character_name_for_log)

    def get_display_name(self) -> str:
        """Restituisce il nome leggibile del tipo di bisogno."""
        # Utilizza la property display_name dell'enum NeedType se disponibile,
        # altrimenti formatta il nome del membro dell'enum.
        if hasattr(self.need_type, 'display_name_it'): # Adattato alla tua enum
            return self.need_type.display_name_it()
        return self.need_type.name.capitalize().replace("_", " ")

    def __str__(self) -> str:
        return f"{self.get_display_name()}: {self.value:.1f}"