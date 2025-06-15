# core/utils/anthalys_circadian_model.py
import math
from core.config import time_config
# from .external.circadian import models # Importiamo i modelli dalla libreria che hai inserito

class AnthalysCircadianModel:
    """
    Un adattatore che usa la libreria 'circadian' ma la adatta
    al nostro giorno di 28 ore.
    """
    def __init__(self):
        # Possiamo inizializzare qui il modello della libreria se necessario
        # Per ora, le sue funzioni sembrano essere statiche
        pass

    def get_rhythm_value(self, anthalys_hour_float: float) -> float:
        """
        Calcola il valore del ritmo circadiano.
        Restituisce un valore tra -1 (massima sonnolenza) e +1 (massima veglia).
        """
        # Ipotizziamo un picco di veglia alle 14:00 e un picco di sonno alle 2:00
        peak_hour = 14.0
        day_duration = time_config.HXD # Nostre 28 ore

        # Calcola la fase del coseno per un ciclo di 28 ore
        phase = (anthalys_hour_float - peak_hour) * (math.pi / (day_duration / 2))

        return math.cos(phase)

    # def get_rhythm_value(self, anthalys_hour_float: float) -> float:
    #     """
    #     Calcola il valore del ritmo circadiano per un'ora di Anthalys.
    #     Restituisce un valore tra -1 (massima sonnolenza) e +1 (massima veglia).
    #     """
    #     # 1. Scala l'ora di Anthalys (0-28) a un'ora equivalente su 24 ore
    #     day_duration_anthalys = time_config.HXD # Nostre 28 ore
    #     equivalent_24h_hour = (anthalys_hour_float / day_duration_anthalys) * 24.0

    #     # 2. Usa una funzione della libreria circadian con l'ora scalata
    #     # Ipotizziamo di usare il "two_process_model" che è uno standard.
    #     # La funzione 'S' rappresenta il processo circadiano (il nostro ritmo).
    #     # Nota: potremmo dover installare dipendenze come 'numpy' se la libreria le richiede.
    #     try:
    #         # La funzione si aspetta il tempo in ore
    #         rhythm_value = models.two_process_model.S(t=equivalent_24h_hour, C_max=0.97, g=0.21, tau_c=24.2, beta=0.013)
    #         # Normalizziamo il risultato tra -1 e 1 se necessario (dipende da cosa restituisce la libreria)
    #         return rhythm_value
    #     except Exception as e:
    #         # Se la libreria fallisce, torniamo a un calcolo di default
    #         print(f"[Circadian WARN] Errore nella libreria esterna: {e}. Uso il fallback a coseno.")
    #         # Fallback alla funzione a coseno che avevamo progettato
    #         return math.cos((anthalys_hour_float - 14.0) * (math.pi / 14.0))