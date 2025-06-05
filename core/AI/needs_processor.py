# core/AI/needs_processor.py
"""
Gestione avanzata dei bisogni NPC
"""
from typing import TYPE_CHECKING, List, Optional # Aggiunto Optional
from core import settings
from core.enums import NeedType
from core.AI.problem_definitions import Problem, ProblemType
from core.config import npc_config # Importa npc_config
# from core.modules.needs.common_needs import IntimacyNeed # Rimosso se update_needs è pass

if TYPE_CHECKING:
    from core.character import Character
    # from core.modules.time_manager import TimeManager

class NeedsProcessor:
    def update_needs(self, npc, time_delta): # time_delta qui è il numero di tick
        # Calcola il decadimento basato sul tempo
        # La logica attiva di questo metodo è attualmente gestita da AICoordinator
        # che chiama direttamente npc.update_needs().
        # Questa sezione è un placeholder per quando NeedsProcessor implementerà
        # la sua logica di aggiornamento dei bisogni più dettagliata.

        # Logica futura di riferimento (attualmente commentata e corretta):
        """
        for need_type_enum_member in npc.needs: # Itera sulle chiavi dell'Enum nel dizionario npc.needs
            need_obj = npc.needs.get(need_type_enum_member)
            if need_obj:
                # Il metodo decay dell'oggetto BaseNeed si aspetta fraction_of_hour
                fraction_of_hour = time_delta / settings.IXH # settings.IXH dovrebbe essere definito
                
                # Accedi a NeedType tramite l'Enum importato, non da settings
                if need_type_enum_member == NeedType.INTIMACY and isinstance(need_obj, IntimacyNeed):
                    need_obj.decay(fraction_of_hour, npc.get_age_in_days(), npc.name)
                elif hasattr(need_obj, 'decay'): # Verifica se il bisogno ha un metodo decay
                    need_obj.decay(fraction_of_hour, npc.name)
        
        # Le seguenti chiamate sono per una futura implementazione più dettagliata
        # self._apply_environmental_effects(npc, simulation_context) # simulation_context sarebbe necessario
        # self._apply_trait_effects(npc)
        # _clamp_needs non è necessario qui perché è gestito in BaseNeed.change_value
        """
        pass

    def _apply_environmental_effects(self, npc, simulation_context): # Aggiunto simulation_context se necessario
        """Effetti dell'ambiente sui bisogni"""
        # Esempio di come potrebbe essere (richiede accesso alla simulazione):
        # location = simulation_context.get_location_by_id(npc.current_location_id)
        # if location and location.is_outdoor and simulation_context.weather_manager.is_raining: # Assumendo un weather_manager
        #     npc.change_need_value(NeedType.COMFORT, -0.1 * time_delta) # Esempio
        pass

    def _apply_trait_effects(self, npc):
        """Effetti dei tratti sui bisogni"""
        # Esempio:
        # if npc.has_trait("HIGH_METABOLISM"): # Assumendo un metodo npc.has_trait()
        #     current_hunger = npc.get_need_value(NeedType.HUNGER)
        #     if current_hunger is not None:
        #         # Questa è una modifica diretta, non un tasso di decadimento aggiuntivo
        #         # La logica dei tratti che modificano i tassi di decadimento andrebbe in BaseNeed.decay o qui
        #         pass
        pass

    # _clamp_needs non è più necessario qui perché BaseNeed.change_value() già gestisce il clamping.

    def _get_critical_need_modifier(self, need_value: float) -> float:
        critical_threshold = npc_config.NEED_CRITICAL_THRESHOLD 
        if need_value <= critical_threshold:
            return npc_config.CRITICAL_NEED_THRESHOLD_MODIFIER 
        return 1.0

    def identify_need_problems(self, npc: 'Character', current_sim_time: Optional[float] = None) -> List[Problem]:
        problems: List[Problem] = []
        if not npc.needs:
            return problems

        low_need_threshold = npc_config.NEED_LOW_THRESHOLD

        for need_type, need_obj in npc.needs.items():
            current_value = need_obj.get_value()

            if current_value < low_need_threshold:
                max_val = npc_config.NEED_MAX_VALUE
                normalized_value = current_value / max_val
                # Accedi a NEED_WEIGHTS da npc_config
                urgency_score = (1.0 - normalized_value) * \
                                npc_config.NEED_WEIGHTS.get(need_type, 0.5) * \
                                self._get_critical_need_modifier(current_value)

                problem_details = {
                    "need": need_type,
                    "current_value": current_value,
                    "target_threshold": low_need_threshold
                }

                problem = Problem(
                    npc_id=npc.npc_id,
                    problem_type=ProblemType.LOW_NEED,
                    urgency=max(0.0, min(1.0, urgency_score)), 
                    details=problem_details,
                    timestamp=current_sim_time
                )
                problems.append(problem)

                if settings.DEBUG_MODE:
                    print(f"    [NeedsProcessor] Problema Rilevato per {npc.name}: {need_type.name} basso ({current_value:.1f}), Urgenza: {problem.urgency:.2f}")

        problems.sort(key=lambda p: p.urgency, reverse=True)
        return problems

    # Il NeedsProcessor potrebbe anche mantenere il metodo per il decadimento dei bisogni
    # se vogliamo centralizzare tutta la logica dei bisogni qui, come da TODO I.2.c.
    # def process_needs_decay(self, npc: 'Character', time_manager: 'TimeManager', ticks_elapsed: int):
    #     # Logica di Character.update_needs() spostata qui
    #     pass 

    def get_priority_need(self, npc):
        """Restituisce il bisogno più urgente"""
        if hasattr(npc, 'get_lowest_need'):
            return npc.get_lowest_need()
        return None