# core/SoNet/sonet_portal.py
from typing import TYPE_CHECKING, List, Dict, Any, Set, Optional # Aggiungi Optional e gli altri tipi generici

"""
Modulo per la gestione del portale SoNet, il sistema unico dei servizi
al cittadino di Anthalys.
Riferimento: TODO.md, Sezione XXIV.
"""

from core import settings
from core.enums import *

if TYPE_CHECKING:
    from core.character import Character

# Potremmo definire un numero massimo di suggerimenti da restituire
MAX_MATCHMAKING_SUGGESTIONS = 3 # TODO: Forse in settings.py

class SoNetPortal:
    def __init__(self, simulation_instance=None):
        if settings.DEBUG_MODE:
            print("  [SoNetPortal INIT] Istanza di SoNetPortal creata.")
        self.simulation = simulation_instance

    def npc_uses_sonet(self, npc_id: str, service_key: str, parameters: dict = None) -> dict:
        if not self.simulation:
            if settings.DEBUG_MODE: print("  [SoNetPortal ERROR] Istanza simulazione mancante!")
            return {"status": "error", "message": "Contesto simulazione non disponibile."}

        if settings.DEBUG_MODE:
            print(f"  [SoNetPortal] NPC '{npc_id}' usa servizio: '{service_key}'")

        if service_key == "view_did_info":
            return self._handle_view_did_info(npc_id)
        elif service_key == "read_notifications":
            return self._handle_read_notifications(npc_id)
        elif service_key == "amori_curati_social_hubs_phase1":
            return self._handle_amori_curati_social_hubs_phase1(npc_id)
        elif service_key == "amori_curati_matchmaking_phase2": 
            return self._handle_amori_curati_matchmaking_phase2(npc_id)
        elif service_key == "amori_curati_friend_connect": # NUOVO SERVIZIO "TROVA AMICI"
            return self._handle_amori_curati_friend_connect(npc_id)
        elif service_key == "amori_curati_friend_connect": # NUOVO SERVIZIO "TROVA AMICI"
            return self._handle_amori_curati_friend_connect(npc_id) # 'parameters' potrebbe essere usato in futuro per filtri amici
        else:
            message = f"Servizio SoNet '{service_key}' non riconosciuto."
            if settings.DEBUG_MODE: print(f"  [SoNetPortal] {message}")
            return {"status": "error", "message": message}

    def _handle_view_did_info(self, npc_id: str) -> dict:
        npc = self.simulation.get_npc_by_id(npc_id)
        if not npc: return {"status": "error", "message": f"NPC '{npc_id}' non trovato."}
        message = f"L'NPC '{npc.name}' visualizza info DID (placeholder)."
        did_data = {"nome_completo": npc.name, "cip": f"ATH-{npc.npc_id[-4:]}-{str(npc.get_age_in_days()%10000).zfill(4)}-X", "status_portale": "Attivo"}
        return {"status": "success_placeholder", "message": message, "data": {"did_info": did_data}}

    def _handle_read_notifications(self, npc_id: str) -> dict:
        npc = self.simulation.get_npc_by_id(npc_id)
        if not npc: return {"status": "error", "message": f"NPC '{npc_id}' non trovato."}
        message = f"L'NPC '{npc.name}' legge notifiche (placeholder)."
        notifications_data = [f"Benvenuto, {npc.name}!", "Promemoria pagamento.", "Nuovo episodio 'Cronache'."]
        return {"status": "success_placeholder", "message": message, "data": {"notifications": notifications_data}}

    def _handle_amori_curati_social_hubs_phase1(self, npc_id: str) -> dict:
        # ... (come implementato precedentemente, usa self.simulation.find_social_hubs) ...
        if settings.DEBUG_MODE: print(f"    [SoNetPortal Service] NPC '{npc_id}' richiede 'Amori Curati Fase 1'.")
        npc: Character | None = self.simulation.get_npc_by_id(npc_id)
        if not npc: return {"status": "error", "message": f"NPC ID '{npc_id}' non trovato."}
        if npc.get_age_in_days() < settings.AMORI_CURATI_PHASE1_ACCESS_MIN_AGE_DAYS:
            return {"status": "ineligible_age", "message": "Servizio Fase 1 non disponibile per la tua età."}
        npc_interests: set[Interest] = npc.get_interests()
        if not npc_interests: return {"status": "no_interests_profiled", "message": "Nessun interesse profilato."}
        suitable_hubs: list[dict] = self.simulation.find_social_hubs(target_interests=npc_interests)
        if not suitable_hubs: return {"status": "no_suggestions_found", "message": "Nessun hub trovato per i tuoi interessi."}
        suggestions = [{"name": h.get("name"), "type": h.get("activity_type_descriptor"), "description": h.get("description")} for h in suitable_hubs]
        return {"status": "success", "message": "Ecco alcuni suggerimenti di luoghi sociali:", "data": {"suggested_hubs": suggestions}}

    def _handle_amori_curati_matchmaking_phase2(self, npc_id: str) -> dict:
        """
        Gestisce la richiesta "Amori Curati" Fase 2: suggerisce potenziali partner
        basandosi su un'analisi più mirata.
        Accessibile da settings.AMORI_CURATI_PHASE2_ACCESS_MIN_AGE_DAYS.
        """
        if settings.DEBUG_MODE:
            print(f"    [SoNetPortal Service] NPC '{npc_id}' richiede 'Amori Curati Matchmaking Fase 2'.")

        # 1. Recuperare l'NPC richiedente
        requesting_npc: Character | None = self.simulation.get_npc_by_id(npc_id)
        if not requesting_npc:
            return {"status": "error", "message": f"NPC con ID '{npc_id}' non trovato."}

        # 2. Verificare l'età per l'accesso alla Fase 2
        if requesting_npc.get_age_in_days() < settings.AMORI_CURATI_PHASE2_ACCESS_MIN_AGE_DAYS:
            return {
                "status": "ineligible_age",
                "message": (f"Servizio 'Amori Curati Fase 2' non disponibile. "
                            f"Età richiesta: {settings.AMORI_CURATI_PHASE2_ACCESS_MIN_AGE_YEARS} anni, "
                            f"età attuale: {requesting_npc.get_age_in_years_float():.1f} anni.")
            }
        
        # Se l'NPC è asessuale E aromantico, questa funzione potrebbe non essere ciò che cerca
        if requesting_npc.is_asexual() and requesting_npc.is_aromantic():
            return {
                "status": "service_not_applicable",
                "message": "Questo servizio di matchmaking potrebbe non essere in linea con il tuo profilo attuale."
            }

        # 3. Ottenere la lista di candidati preliminari dalla simulazione
        # Questo metodo applica già filtri su età, stato sentimentale e orientamento di base
        potential_candidates: List['Character'] = self.simulation.get_eligible_dating_candidates(requesting_npc)

        if not potential_candidates:
            return {
                "status": "no_candidates_found",
                "message": "Al momento non abbiamo trovato profili compatibili. Il mondo di Anthalys è vasto, riprova più tardi!"
            }

        # 4. Applicare "Algoritmi più Mirati" (Punteggio di Compatibilità)
        scored_candidates: List[Dict[str, Any]] = []
        req_interests = requesting_npc.get_interests()
        req_aspiration = requesting_npc.get_aspiration()

        for candidate in potential_candidates:
            compatibility_score = 0
            
            # a. Punteggio Interessi Comuni
            shared_interests = req_interests.intersection(candidate.get_interests())
            compatibility_score += len(shared_interests) * 10 # Es. 10 punti per interesse comune

            # b. Punteggio Aspirazioni Comuni (se definite)
            cand_aspiration = candidate.get_aspiration()
            if req_aspiration and cand_aspiration and req_aspiration == cand_aspiration:
                compatibility_score += 20 # Bonus se le aspirazioni principali coincidono

            # c. TODO [FUTURO]: Punteggio basato sulla compatibilità dei Tratti (TraitName)
            #    Quando i tratti saranno implementati in Character, potremo aggiungere logica qui.
            #    Es. tratto "Romantico" con "Romantico" = +punti, "Cinico" con "Romantico" = -punti.
            
            # d. TODO [FUTURO]: Malus per differenze di età elevate (anche se già filtrato, potremmo penalizzare i limiti)
            
            scored_candidates.append({
                "npc_object": candidate, # Teniamo l'oggetto per accedere ai dati dopo l'ordinamento
                "score": compatibility_score,
                "shared_interests_names": [i.name for i in shared_interests] # Per il messaggio finale
            })

        # 5. Ordinare i candidati per punteggio (dal più alto al più basso)
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)

        # 6. Selezionare i migliori N suggerimenti
        top_suggestions_data = scored_candidates[:MAX_MATCHMAKING_SUGGESTIONS]

        if not top_suggestions_data:
             return {"status": "no_strong_matches_found", "message": "Non sono emerse compatibilità particolarmente forti con le tue preferenze."}

        # 7. Formattare il risultato per l'NPC
        final_suggestions_for_npc = []
        for suggestion_data in top_suggestions_data:
            cand_obj: Character = suggestion_data["npc_object"]
            final_suggestions_for_npc.append({
                "name": cand_obj.name, "age_years": f"{cand_obj.get_age_in_years_float():.0f}",
                "gender": cand_obj.gender.display_name_it(),
                "brief_description": f"Interessi comuni: {', '.join(suggestion_data['shared_interests_names']) if suggestion_data['shared_interests_names'] else 'da scoprire'}.",
                "compatibility_hint": f"Affinità preliminare: {suggestion_data['score']}"})
            
        return {
            "status": "success",
            "message": "In base alle tue preferenze, abbiamo analizzato alcuni profili:",
            "data": {"suggested_partners": final_suggestions_for_npc}
        }

    def _handle_amori_curati_friend_connect(self, npc_id: str) -> dict:
        """
        Gestisce la richiesta "Trova Amici": suggerisce potenziali amici
        basandosi principalmente su interessi comuni e fascia d'età.
        Accessibile da settings.FRIEND_CONNECT_MIN_ACCESS_AGE_DAYS.
        """
        if settings.DEBUG_MODE:
            print(f"    [SoNetPortal Service] NPC '{npc_id}' richiede 'Trova Amici'.")

        # 1. Recuperare l'NPC richiedente
        requesting_npc: Optional['Character'] = self.simulation.get_npc_by_id(npc_id)
        if not requesting_npc:
            return {"status": "error", "message": f"NPC con ID '{npc_id}' non trovato."}

        # 2. Verificare l'età per l'accesso al servizio "Trova Amici"
        if requesting_npc.get_age_in_days() < settings.FRIEND_CONNECT_MIN_ACCESS_AGE_DAYS:
            min_age_years = settings.FRIEND_CONNECT_MIN_ACCESS_AGE_YEARS
            return {
                "status": "ineligible_age",
                "message": (f"Servizio 'Trova Amici' non disponibile. "
                            f"Età richiesta: {min_age_years} anni, "
                            f"età attuale: {requesting_npc.get_age_in_years_float():.1f} anni.")
            }
        
        # 3. Ottenere la lista di candidati preliminari dalla simulazione
        # Questo metodo usa già filtri per età e auto-esclusione specifici per amicizia
        potential_friends: List['Character'] = self.simulation.get_potential_friend_candidates(requesting_npc)

        if not potential_friends:
            return {
                "status": "no_friend_candidates_found",
                "message": "Al momento non abbiamo trovato profili particolarmente affini per un'amicizia. Prova a esplorare i Social Hub o a coltivare nuovi interessi!"
            }

        # 4. Applicare "Algoritmo Mirato" per Amicizia (Punteggio di Compatibilità)
        scored_friends: List[Dict[str, Any]] = []
        req_interests = requesting_npc.get_interests()
        # req_life_stage = requesting_npc.life_stage # Per futuro bonus stessa LifeStage

        for candidate_friend in potential_friends:
            friendship_score = 0
            
            # a. Punteggio Interessi Comuni (molto importante per amicizia)
            shared_interests = req_interests.intersection(candidate_friend.get_interests())
            friendship_score += len(shared_interests) * 15 # Ponderazione per interessi amici

            # b. TODO [FUTURO]: Bonus per LifeStage simile o adiacente
            # if req_life_stage and candidate_friend.life_stage and \
            #    abs(req_life_stage.value - candidate_friend.life_stage.value) <= 1: # Esempio di vicinanza
            #    friendship_score += 5
            
            # c. TODO [FUTURO]: Punteggio basato sulla compatibilità dei Tratti (TraitName)
            #    Es. due "ESTROVERSI" potrebbero avere un bonus, ecc.

            # d. TODO [FUTURO]: Malus se esiste già una relazione negativa (ENEMY)
            
            scored_friends.append({
                "npc_object": candidate_friend,
                "score": friendship_score,
                "shared_interests_names": [i.name for i in shared_interests]
            })

        # 5. Ordinare i candidati per punteggio (dal più alto al più basso)
        scored_friends.sort(key=lambda x: x["score"], reverse=True)

        # 6. Selezionare i migliori N suggerimenti
        # Usiamo la stessa costante MAX_MATCHMAKING_SUGGESTIONS per ora, o ne creiamo una nuova.
        top_friend_suggestions_data = scored_friends[:settings.MAX_MATCHMAKING_SUGGESTIONS] 

        # Se anche i migliori hanno score 0 (nessun interesse comune), messaggio specifico
        if not top_friend_suggestions_data or all(s['score'] == 0 for s in top_friend_suggestions_data):
             return {
                "status": "no_strong_friend_matches_found",
                "message": "Non emergono particolari affinità di interessi con altri utenti per formare nuove amicizie in questo momento."
            }

        # 7. Formattare il risultato per l'NPC
        final_friend_suggestions = []
        for suggestion_data in top_friend_suggestions_data:
            cand_obj: Character = suggestion_data["npc_object"]
            shared_interests_str = ', '.join(suggestion_data['shared_interests_names'])
            profile = {
                "name": cand_obj.name,
                "age_years": f"{cand_obj.get_age_in_years_float():.0f}",
                "gender": cand_obj.gender.display_name_it(),
                "life_stage": cand_obj.life_stage.display_name_it() if cand_obj.life_stage else "N/D",
                "shared_interests_count": len(suggestion_data["shared_interests_names"]),
                "shared_interests_preview": (f"Condividete interessi come: {shared_interests_str}." 
                                             if shared_interests_str else 
                                             "Potreste scoprire passioni in comune!"),
                "compatibility_hint": f"Potenziale di amicizia (interessi): {suggestion_data['score']}"
            }
            final_friend_suggestions.append(profile)
            
        return {
            "status": "success",
            "message": "Abbiamo trovato alcuni profili che potrebbero fare al caso tuo per una nuova amicizia:",
            "data": {"suggested_friends": final_friend_suggestions}
        }

    # E il dispatcher in npc_uses_sonet verrebbe chiamato così:
    # elif service_key == "amori_curati_matchmaking_phase2":
    #     return self._handle_amori_curati_matchmaking_phase2(npc_id, parameters) # Passa i 'parameters'

# --- Blocco di Test per sonet_portal.py ---
if __name__ == '__main__':
    print("--- Test diretto di core/SoNet/sonet_portal.py ---")
    
    # Setup Mock (come nella risposta precedente, assicurati che MockCharacter supporti
    # tutti gli attributi e metodi usati, inclusi quelli per l'amicizia e aspirazioni)
    # Per brevità, non ripeto qui l'intero blocco MockSimulation e MockCharacter,
    # ma andrebbe esteso per testare anche il nuovo servizio "amori_curati_friend_connect".

    # Esempio di come potresti estendere il test (aggiungendo a MockSimulationForSoNetFull)
    class MockCharacterForSoNetFriendTest(Character): # Usa la classe reale per testare se possibile
        pass # Già definita in modo completo

    class MockSimulationForSoNetFriendTest: # Rinomina per chiarezza
        def __init__(self):
            self.npcs_for_test: Dict[str, MockCharacterForSoNetFriendTest] = {}
            self._initialize_test_npcs_for_friends()
        
        def _initialize_test_npcs_for_friends(self):
            # Richiedente per amicizia (16 anni)
            self.elena_cerca_amici = MockCharacterForSoNetFriendTest(
                "elena_amici_req", "Elena Amica Richiedente", Gender.FEMALE, 16 * settings.DXY,
                initial_interests={Interest.MUSIC_LISTENING, Interest.GAMING, Interest.READING},
                initial_aspiration=AspirationType.SOCIAL_BUTTERFLY
            )
            self.add_npc_for_test(self.elena_cerca_amici)

            # Candidati amici
            self.add_npc_for_test(MockCharacterForSoNetFriendTest(
                "marco_amico_cand", "Marco Gamer Amico", Gender.MALE, 17 * settings.DXY,
                initial_interests={Interest.GAMING, Interest.TECHNOLOGY} # Condivide GAMING
            ))
            self.add_npc_for_test(MockCharacterForSoNetFriendTest(
                "laura_amica_cand", "Laura Lettrice Amica", Gender.FEMALE, 15 * settings.DXY,
                initial_interests={Interest.READING, Interest.VISUAL_ARTS} # Condivide LETTURA
            ))
            self.add_npc_for_test(MockCharacterForSoNetFriendTest( # Nessun interesse comune
                "luca_amico_cand", "Luca Sportivo Amico", Gender.MALE, 14 * settings.DXY,
                initial_interests={Interest.SPORTS_ACTIVE, Interest.PHOTOGRAPHY} 
            ))
            self.add_npc_for_test(MockCharacterForSoNetFriendTest( # Troppo grande per FRIEND_MAX_AGE_DIFFERENCE_YEARS
                "sara_adulta_amica_cand", "Sara Adulta (non amica)", Gender.FEMALE, 
                (16 + settings.FRIEND_MAX_AGE_DIFFERENCE_YEARS + 1) * settings.DXY,
                initial_interests={Interest.GAMING}
            ))

        def add_npc_for_test(self, npc: MockCharacterForSoNetFriendTest):
            self.npcs_for_test[npc.npc_id] = npc

        def get_npc_by_id(self, npc_id_to_find: str) -> Optional['Character']: # Modificato per coerenza
            return self.npcs_for_test.get(npc_id_to_find)

        def get_potential_friend_candidates(self, requesting_npc: 'Character') -> list['Character']:
            # Mock della logica di Simulation.get_potential_friend_candidates
            eligible = []
            req_age_days = requesting_npc.get_age_in_days()
            min_cand_age = settings.FRIEND_CONNECT_MIN_ACCESS_AGE_DAYS
            max_age_diff = settings.FRIEND_MAX_AGE_DIFFERENCE_YEARS * settings.DXY
            for cand_npc in self.npcs_for_test.values():
                if cand_npc.npc_id == requesting_npc.npc_id: continue
                if cand_npc.get_age_in_days() < min_cand_age: continue
                if abs(cand_npc.get_age_in_days() - req_age_days) > max_age_diff: continue
                eligible.append(cand_npc)
            if settings.DEBUG_MODE: print(f"  [MockSim FriendCandidates] Per {requesting_npc.name}, mock ha trovato: {[c.name for c in eligible]}")
            return eligible
        
        # Mock per gli altri metodi chiamati da SoNetPortal se necessario per altri test
        def get_eligible_dating_candidates(self, requesting_npc: 'Character', search_preferences = None) -> list['Character']: return []
        def find_social_hubs(self, target_interests: Set[Interest]) -> list[dict]: return []


    print("\n[Test SoNet - Trova Amici] Creazione istanze mock...")
    # Setup di settings per il test (come nella risposta precedente)
    # Assicurati che FRIEND_CONNECT_MIN_ACCESS_AGE_DAYS, FRIEND_MAX_AGE_DIFFERENCE_YEARS, MAX_MATCHMAKING_SUGGESTIONS
    # e DXY siano definiti nell'oggetto settings per questo test.
    if not hasattr(settings, 'DXY'): settings.DXY = 432 # Fallback
    if not hasattr(settings, 'FRIEND_CONNECT_MIN_ACCESS_AGE_YEARS'): settings.FRIEND_CONNECT_MIN_ACCESS_AGE_YEARS = 14
    if not hasattr(settings, 'FRIEND_CONNECT_MIN_ACCESS_AGE_DAYS'): 
        settings.FRIEND_CONNECT_MIN_ACCESS_AGE_DAYS = settings.FRIEND_CONNECT_MIN_ACCESS_AGE_YEARS * settings.DXY
    if not hasattr(settings, 'FRIEND_MAX_AGE_DIFFERENCE_YEARS'): settings.FRIEND_MAX_AGE_DIFFERENCE_YEARS = 10
    if not hasattr(settings, 'MAX_MATCHMAKING_SUGGESTIONS'): settings.MAX_MATCHMAKING_SUGGESTIONS = 3
    # Per le altre fasi di Amori Curati, se il mock le chiama
    if not hasattr(settings, 'AMORI_CURATI_PHASE1_ACCESS_MIN_AGE_DAYS'): settings.AMORI_CURATI_PHASE1_ACCESS_MIN_AGE_DAYS = 18 * settings.DXY
    if not hasattr(settings, 'AMORI_CURATI_PHASE2_ACCESS_MIN_AGE_DAYS'): settings.AMORI_CURATI_PHASE2_ACCESS_MIN_AGE_DAYS = 25 * settings.DXY


    mock_sim_friends_test = MockSimulationForSoNetFriendTest()
    sonet_portal_friends_test_instance = SoNetPortal(simulation_instance=mock_sim_friends_test)

    print("\n[Test SoNet - Trova Amici] Chiamata per Elena Curiosa (16 anni):")
    result_friends_elena = sonet_portal_friends_test_instance.npc_uses_sonet(
        mock_sim_friends_test.elena_cerca_amici.npc_id, 
        "amori_curati_friend_connect"
    )
    print(f"Status: {result_friends_elena.get('status')}")
    print(f"Message: {result_friends_elena.get('message')}")
    if result_friends_elena.get('data') and result_friends_elena['data'].get('suggested_friends'):
        print("Amici Suggeriti per Elena:")
        for friend_profile in result_friends_elena['data']['suggested_friends']:
            print(f"  - Nome: {friend_profile['name']}, Età: {friend_profile['age_years']}, "
                  f"Genere: {friend_profile['gender']}, Fase Vita: {friend_profile['life_stage']}")
            print(f"    Interessi Comuni ({friend_profile.get('shared_interests_count')}): {friend_profile['shared_interests_preview']}")
            print(f"    Hint Compatibilità: {friend_profile['compatibility_hint']}")
    
    print("\n--- Fine test diretto di core/SoNet/sonet_portal.py ---")
