# core/AI/social_manager.py
from typing import TYPE_CHECKING, Optional
import random

# Import necessari dalle tue definizioni
from core.enums import SocialInteractionType, RelationshipType, NeedType, Gender # Aggiunto Gender per _select_interaction_type
from core.modules.actions.social_actions import SocializeAction
from core import settings

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    # from core.modules.relationships.relationship_models import RelationshipInfo # Se la usi direttamente qui

class SocialManager:
    def __init__(self, simulation_context: 'Simulation'):
        """
        Inizializza il SocialManager.

        Args:
            simulation_context (Simulation): L'istanza della simulazione principale.
        """
        self.simulation_context: 'Simulation' = simulation_context
        if settings.DEBUG_MODE:
            print("  [SocialManager INIT] SocialManager creato.")

    def _select_interaction_type(self, initiator: 'Character', target: 'Character') -> SocialInteractionType:
        """
        Seleziona un tipo di interazione sociale appropriato tra due NPC.
        Questa è la tua logica, come l'hai fornita.
        """
        # TODO: Implementare una logica più sofisticata basata su relazione, tratti, umore, contesto.
        relationship_info = initiator.get_relationship_with(target.npc_id) # Usa il tuo metodo get_relationship_with
        
        possible_interactions = [
            # SocialInteractionType.CHAT, # Hai commentato CHAT, lo lascio così
            SocialInteractionType.TELL_JOKE, 
            SocialInteractionType.COMPLIMENT
        ]
        
        # Assicurati che i membri dell'Enum SocialInteractionType esistano!
        if relationship_info:
            if relationship_info.score > 30 and hasattr(SocialInteractionType, 'DEEP_CONVERSATION'):
                possible_interactions.append(SocialInteractionType.DEEP_CONVERSATION)
            
            # Verifica attrazione prima di aggiungere FLIRT
            initiator_is_attracted = False
            if hasattr(initiator, 'get_sexual_attraction') and hasattr(initiator, 'get_romantic_attraction'):
                initiator_is_attracted = (target.gender in initiator.get_sexual_attraction() or \
                                        target.gender in initiator.get_romantic_attraction())

            if relationship_info.score > 10 and initiator_is_attracted and hasattr(SocialInteractionType, 'FLIRT'):
                possible_interactions.append(SocialInteractionType.FLIRT)
            
            if relationship_info.score < -20 and hasattr(SocialInteractionType, 'ARGUE'):
                possible_interactions.append(SocialInteractionType.ARGUE)

        if hasattr(SocialInteractionType, 'PROPOSE_INTIMACY') and SocialInteractionType.PROPOSE_INTIMACY in possible_interactions:
            possible_interactions.remove(SocialInteractionType.PROPOSE_INTIMACY)
            
        if not possible_interactions: 
            # Fallback se la lista è vuota (assicurati che COMPLIMENT esista nell'enum)
            if hasattr(SocialInteractionType, 'COMPLIMENT'):
                return SocialInteractionType.COMPLIMENT
            elif SocialInteractionType: # Se COMPLIMENT non c'è, prendi il primo disponibile
                try:
                    return list(SocialInteractionType)[0]
                except IndexError: # L'enum è completamente vuoto, situazione critica
                    if settings.DEBUG_MODE: print(f"    [SocialManager CRITICAL WARN] Enum SocialInteractionType è vuoto!")
                    # In un caso reale, potresti sollevare un'eccezione o avere un default più sicuro
                    raise ValueError("Enum SocialInteractionType è vuoto o non configurato.")
            else: # SocialInteractionType non è un Enum valido o è None
                raise ValueError("SocialInteractionType non è un Enum valido.")


        return random.choice(possible_interactions)

    def _update_relationship_from_interaction(self, 
                                            initiator: 'Character', 
                                            target: 'Character', 
                                            interaction_action: SocializeAction # Ora è un'istanza di SocializeAction
                                            ):
        """
        Questo metodo potrebbe essere chiamato da SocializeAction.on_finish() se vuoi centralizzare
        ulteriormente la logica di aggiornamento delle relazioni o triggerare eventi specifici
        del SocialManager dopo un'interazione.
        La tua attuale SocializeAction.on_finish() sembra già gestire gran parte di questo.
        """
        if not initiator or not target or not interaction_action:
            return

        if settings.DEBUG_MODE:
            print(f"    [SocialManager] Registrazione/Post-elaborazione interazione "
                f"'{interaction_action.interaction_type.name}' tra {initiator.name} e {target.name}.")
        
        # Esempio: Potresti voler registrare statistiche globali sulle interazioni,
        # o triggerare eventi più ampi basati sull'esito (se l'azione avesse un esito esplicito).
        # La logica principale di modifica dei punteggi di relazione e dei bisogni
        # è già nel tuo SocializeAction.on_finish().
        pass

    def attempt_social_interaction(self, initiator: 'Character', target: 'Character'):
        """
        Metodo pubblico per un NPC (iniziatore) che tenta di avviare 
        un'interazione sociale con un altro NPC (target).
        """
        if not initiator or not target or initiator == target:
            if settings.DEBUG_MODE:
                print(f"    [SocialManager attempt_social_interaction WARN] Iniziatore o target non validi o uguali.")
            return

        # 1. Seleziona il tipo di interazione
        # _select_interaction_type deve restituire un SocialInteractionType valido
        interaction_type = self._select_interaction_type(initiator, target)
        
        if interaction_type is None: # Aggiunto controllo esplicito
            if settings.DEBUG_MODE:
                print(f"    [SocialManager attempt_social_interaction WARN] Nessun tipo di interazione valido selezionato per {initiator.name} con {target.name}.")
            return

        if settings.DEBUG_MODE:
            print(f"  [SocialManager] {initiator.name} (ID: {initiator.npc_id}) tenta interazione '{interaction_type.name}' con {target.name} (ID: {target.npc_id}).")

        # 2. Crea l'istanza dell'azione SocializeAction
        #    Assumiamo che SocializeAction gestisca internamente la durata e gli effetti
        #    basati su interaction_type e configurazioni lette da settings (come nel tuo codice).
        #    Se vuoi disaccoppiare SocializeAction da settings, dovresti passare quelle config qui.
        social_action_instance = SocializeAction(
            npc=initiator,
            target_npc=target,
            interaction_type=interaction_type,
            simulation_context=self.simulation_context
            # duration_ticks è opzionale in SocializeAction; se omesso, SocializeAction
            # userà i suoi default interni o quelli letti da settings.
        )

        # 3. Verifica se l'azione è valida e aggiungila alla coda dell'iniziatore
        if social_action_instance.is_valid():
            initiator.add_action_to_queue(social_action_instance)
            if settings.DEBUG_MODE:
                print(f"    [SocialManager] Azione '{social_action_instance.action_type_name}' (Tipo: {interaction_type.name}) accodata per {initiator.name}.")
            
            # La chiamata a self._update_relationship_from_interaction(initiator, target, social_action_instance)
            # è probabilmente gestita da SocializeAction.on_finish().
            # Se vuoi che SocialManager faccia qualcosa in più DOPO che l'azione è CONCLUSA,
            # dovresti avere un meccanismo di callback o di eventi.
            # Per ora, la responsabilità dell'update è nell'azione stessa.

        elif settings.DEBUG_MODE:
            # action_type_name potrebbe non essere inizializzato se l'enum non è stato trovato in __init__ di SocializeAction
            action_name_for_log = getattr(social_action_instance, 'action_type_name', f"SOCIALIZE_{interaction_type.name}")
            print(f"    [SocialManager] Azione '{action_name_for_log}' con {target.name} non valida per {initiator.name}.")