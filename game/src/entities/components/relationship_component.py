# game/src/entities/components/relationship_component.py
import logging
import math # Non usato attivamente ora, ma potrebbe servire
from typing import Dict, Any, Optional, List, TYPE_CHECKING, Set

# Importa dal package 'game'
from game import config # Per valori di default e soglie

if TYPE_CHECKING:
    from game.src.entities.character import Character # Per il type hint di character_owner e other_npc
    from game.src.modules.game_state_module import GameState # Per accedere alla lista di tutti gli NPC

logger = logging.getLogger(__name__)
DEBUG_RELATIONSHIP = getattr(config, 'DEBUG_AI_ACTIVE', False)

# Valori di default per le relazioni, da config o qui
INITIAL_FRIENDSHIP_VALUE = getattr(config, 'REL_INITIAL_FRIENDSHIP', 0.0)
INITIAL_ROMANCE_VALUE = getattr(config, 'REL_INITIAL_ROMANCE', 0.0)
REL_FRIENDSHIP_MIN = getattr(config, 'REL_FRIENDSHIP_MIN', -100.0)
REL_FRIENDSHIP_MAX = getattr(config, 'REL_FRIENDSHIP_MAX', 100.0)
REL_ROMANCE_MIN = getattr(config, 'REL_ROMANCE_MIN', -100.0)
REL_ROMANCE_MAX = getattr(config, 'REL_ROMANCE_MAX', 100.0)

# Stringhe per i tipi di relazione familiare (possono essere espanse in config.py)
REL_TYPE_MOTHER = getattr(config, "REL_STR_MOTHER", "Madre")
REL_TYPE_FATHER = getattr(config, "REL_STR_FATHER", "Padre")
REL_TYPE_PARENT = getattr(config, "REL_STR_PARENT", "Genitore") # Generico
REL_TYPE_CHILD = getattr(config, "REL_STR_CHILD", "Figlio/a")   # Generico
REL_TYPE_SON = getattr(config, "REL_STR_SON", "Figlio")
REL_TYPE_DAUGHTER = getattr(config, "REL_STR_DAUGHTER", "Figlia")
REL_TYPE_SIBLING = getattr(config, "REL_STR_SIBLING", "Fratello/Sorella")
REL_TYPE_BROTHER = getattr(config, "REL_STR_BROTHER", "Fratello")
REL_TYPE_SISTER = getattr(config, "REL_STR_SISTER", "Sorella")
# ... e altri tipi come Partner, Amico, Nemico, ecc.
REL_TYPE_STRANGER = "Sconosciuto"
REL_TYPE_ACQUAINTANCE = "Conoscente"
REL_TYPE_FRIEND = "Amico"
REL_TYPE_GOOD_FRIEND = "Buon Amico"
REL_TYPE_BEST_FRIEND = "Migliore Amico"
REL_TYPE_ENEMY = "Nemico"
REL_TYPE_PARTNER = "Partner"


class Relationship:
    """Rappresenta la relazione tra il proprietario del componente e un altro NPC specifico."""
    def __init__(self, target_npc_uuid: str,
                 initial_friendship: float = INITIAL_FRIENDSHIP_VALUE,
                 initial_romance: float = INITIAL_ROMANCE_VALUE):
        self.target_npc_uuid: str = target_npc_uuid
        self.friendship_level: float = float(initial_friendship)
        self.romance_level: float = float(initial_romance)
        
        self.is_family_member: bool = False # Flag generico se sono imparentati
        self.family_tie_from_owner_perspective: Optional[str] = None # Es. "Figlio", "Madre" (cosa è il target per l'owner)
        
        self.are_romantic_partners: bool = False # Sposati, fidanzati, coppia fissa
        self.had_first_kiss: bool = False # Esempio di flag romantico
        
        self.days_known_ingame: float = 0.0 # Giorni di gioco da quando si conoscono
        self.last_significant_interaction_time: float = 0.0 # Timestamp di gioco (ore totali)

        # Potresti aggiungere una breve cronologia delle interazioni più importanti
        # self.significant_interaction_log: List[Tuple[float, str]] = [] # (timestamp, descrizione_interazione)

    def modify_friendship(self, amount: float, source_event: str = "Unknown interaction"):
        old_level = self.friendship_level
        self.friendship_level = max(REL_FRIENDSHIP_MIN, min(REL_FRIENDSHIP_MAX, self.friendship_level + amount))
        if DEBUG_RELATIONSHIP and abs(old_level - self.friendship_level) > 0.01:
            logger.debug(f"Rel with {self.target_npc_uuid[-6:]}: Friendship {old_level:.1f} -> {self.friendship_level:.1f} (by {amount:+.1f} from '{source_event}')")

    def modify_romance(self, amount: float, source_event: str = "Unknown interaction"):
        old_level = self.romance_level
        self.romance_level = max(REL_ROMANCE_MIN, min(REL_ROMANCE_MAX, self.romance_level + amount))
        if DEBUG_RELATIONSHIP and abs(old_level - self.romance_level) > 0.01:
            logger.debug(f"Rel with {self.target_npc_uuid[-6:]}: Romance {old_level:.1f} -> {self.romance_level:.1f} (by {amount:+.1f} from '{source_event}')")

    def set_family_tie(self, tie_from_owner: str):
        self.is_family_member = True
        self.family_tie_from_owner_perspective = tie_from_owner

    def get_descriptive_type(self) -> str:
        """Restituisce una stringa descrittiva del tipo di relazione."""
        if self.are_romantic_partners: return REL_TYPE_PARTNER
        if self.is_family_member and self.family_tie_from_owner_perspective: return self.family_tie_from_owner_perspective
        
        # Soglie da config
        if self.friendship_level <= getattr(config, "REL_THRESHOLD_ENEMY", -50): return REL_TYPE_ENEMY
        if self.romance_level >= getattr(config, "REL_THRESHOLD_CRUSH", 30) and self.friendship_level >= 0: return "Cotta" # Semplice
        if self.friendship_level >= getattr(config, "REL_THRESHOLD_BEST_FRIEND", 80): return REL_TYPE_BEST_FRIEND
        if self.friendship_level >= getattr(config, "REL_THRESHOLD_GOOD_FRIEND", 50): return REL_TYPE_GOOD_FRIEND
        if self.friendship_level >= getattr(config, "REL_THRESHOLD_FRIEND", 20): return REL_TYPE_FRIEND
        if self.friendship_level > getattr(config, "REL_THRESHOLD_ACQUAINTANCE", -10) or self.days_known_ingame > 0.1:
            return REL_TYPE_ACQUAINTANCE
        return REL_TYPE_STRANGER

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_npc_uuid": self.target_npc_uuid, # Anche se è la chiave, utile per la ricostruzione
            "friendship_level": self.friendship_level,
            "romance_level": self.romance_level,
            "is_family_member": self.is_family_member,
            "family_tie_from_owner_perspective": self.family_tie_from_owner_perspective,
            "are_romantic_partners": self.are_romantic_partners,
            "had_first_kiss": self.had_first_kiss,
            "days_known_ingame": self.days_known_ingame,
            "last_significant_interaction_time": self.last_significant_interaction_time,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Optional[Relationship]':
        target_uuid = data.get("target_npc_uuid")
        if not target_uuid:
            logger.error("Tentativo di caricare relazione senza target_npc_uuid.")
            return None
            
        instance = cls(
            target_npc_uuid=target_uuid,
            initial_friendship=float(data.get("friendship_level", INITIAL_FRIENDSHIP_VALUE)),
            initial_romance=float(data.get("romance_level", INITIAL_ROMANCE_VALUE))
        )
        instance.is_family_member = data.get("is_family_member", False)
        instance.family_tie_from_owner_perspective = data.get("family_tie_from_owner_perspective")
        instance.are_romantic_partners = data.get("are_romantic_partners", False)
        instance.had_first_kiss = data.get("had_first_kiss", False)
        instance.days_known_ingame = float(data.get("days_known_ingame", 0.0))
        instance.last_significant_interaction_time = float(data.get("last_significant_interaction_time", 0.0))
        return instance


class RelationshipComponent:
    def __init__(self, character_owner: 'Character', owner_uuid: str):
        self.owner: 'Character' = character_owner
        self.owner_uuid: str = owner_uuid
        self.owner_name: str = character_owner.name if character_owner else "NPC Sconosciuto"
        
        # Dizionario: chiave = UUID dell'altro NPC, valore = istanza Relationship
        self.relationships: Dict[str, Relationship] = {}

        # Tracciamento familiare diretto (liste di UUID)
        self.parents_uuids: List[str] = []      # Max 2
        self.children_uuids: List[str] = []
        self.siblings_uuids: List[str] = []     # Fratelli/sorelle con entrambi i genitori in comune
        # self.half_siblings_uuids: List[str] = [] # Fratelli/sorelle con un solo genitore in comune

        if DEBUG_RELATIONSHIP:
            logger.debug(f"RelationshipComponent per {self.owner_name} ({self.owner_uuid[-6:]}) inizializzato.")

    def _ensure_relationship_with(self, target_npc_uuid: str) -> Optional[Relationship]:
        """Ottiene o crea un record di relazione con target_npc_uuid."""
        if target_npc_uuid == self.owner_uuid:
            logger.error(f"Rel Error ({self.owner_name}): Tentativo di creare relazione con se stesso.")
            return None
        if target_npc_uuid not in self.relationships:
            self.relationships[target_npc_uuid] = Relationship(target_npc_uuid)
            if DEBUG_RELATIONSHIP:
                logger.debug(f"Rel ({self.owner_name}): Creata nuova relazione con {target_npc_uuid[-6:]}.")
        return self.relationships[target_npc_uuid]

    def update_relationship_scores(self, target_npc_uuid: str, friendship_change: float = 0, romance_change: float = 0, source_event: str = ""):
        """Modifica i punteggi di amicizia e/o romance con un altro NPC."""
        if target_npc_uuid == self.owner_uuid: return
        rel = self._ensure_relationship_with(target_npc_uuid)
        if rel:
            if friendship_change != 0:
                rel.modify_friendship(friendship_change, source_event)
            if romance_change != 0:
                rel.modify_romance(romance_change, source_event)
            # Aggiorna last_interaction_time se c'è un cambiamento significativo
            if (abs(friendship_change) > 0.1 or abs(romance_change) > 0.1) and \
               hasattr(self.owner, 'game_state_ref') and self.owner.game_state_ref:
                rel.last_significant_interaction_time = self.owner.game_state_ref.current_game_total_sim_hours_elapsed

    def get_relationship_details(self, target_npc_uuid: str) -> Optional[Relationship]:
        """Restituisce l'oggetto Relationship completo con un target, o None."""
        return self.relationships.get(target_npc_uuid)

    # --- Metodi per la Gestione Familiare ---
    def add_parent_link(self, parent_uuid: str, parent_gender: Optional[str] = None):
        """Aggiunge un genitore. Questo è solitamente chiamato sul figlio."""
        if parent_uuid not in self.parents_uuids and len(self.parents_uuids) < 2:
            self.parents_uuids.append(parent_uuid)
            rel_with_parent = self._ensure_relationship_with(parent_uuid)
            if rel_with_parent:
                tie = REL_TYPE_FATHER if parent_gender == "male" else REL_TYPE_MOTHER if parent_gender == "female" else REL_TYPE_PARENT
                rel_with_parent.set_family_tie(tie)
            if DEBUG_RELATIONSHIP: logger.info(f"Rel ({self.owner_name}): {parent_uuid[-6:]} aggiunto come genitore ({tie}).")

    def add_child_link(self, child_uuid: str, child_gender: Optional[str] = None):
        """Aggiunge un figlio. Questo è solitamente chiamato sul genitore."""
        if child_uuid not in self.children_uuids:
            self.children_uuids.append(child_uuid)
            rel_with_child = self._ensure_relationship_with(child_uuid)
            if rel_with_child:
                tie = REL_TYPE_SON if child_gender == "male" else REL_TYPE_DAUGHTER if child_gender == "female" else REL_TYPE_CHILD
                rel_with_child.set_family_tie(tie)
            if DEBUG_RELATIONSHIP: logger.info(f"Rel ({self.owner_name}): {child_uuid[-6:]} aggiunto come figlio ({tie}).")
    
    def add_sibling_link(self, sibling_uuid: str):
        """Aggiunge un fratello/sorella (pieno/a)."""
        if sibling_uuid not in self.siblings_uuids:
            self.siblings_uuids.append(sibling_uuid)
            rel_with_sibling = self._ensure_relationship_with(sibling_uuid)
            if rel_with_sibling:
                rel_with_sibling.set_family_tie(REL_TYPE_SIBLING) # Potrebbe essere più specifico (Brother/Sister) se conosci il genere
            if DEBUG_RELATIONSHIP: logger.info(f"Rel ({self.owner_name}): {sibling_uuid[-6:]} aggiunto come fratello/sorella.")

    def establish_reciprocal_family_links(self, game_state: 'GameState'):
        """
        Itera sui link familiari e cerca di stabilire i reciproci se non esistono.
        Chiamato dopo il caricamento di tutti gli NPC o la creazione di nuove famiglie.
        """
        all_current_npcs = {npc.uuid: npc for npc in game_state.all_npc_characters_list}

        for parent_uuid in list(self.parents_uuids): # Itera su copia se modifichi
            parent_npc = all_current_npcs.get(parent_uuid)
            if parent_npc and parent_npc.relationships:
                if self.owner_uuid not in parent_npc.relationships.children_uuids:
                    parent_npc.relationships.add_child_link(self.owner_uuid, self.owner.gender)

        for child_uuid in list(self.children_uuids):
            child_npc = all_current_npcs.get(child_uuid)
            if child_npc and child_npc.relationships:
                if self.owner_uuid not in child_npc.relationships.parents_uuids:
                    child_npc.relationships.add_parent_link(self.owner_uuid, self.owner.gender)
        
        for sibling_uuid in list(self.siblings_uuids):
            sibling_npc = all_current_npcs.get(sibling_uuid)
            if sibling_npc and sibling_npc.relationships:
                if self.owner_uuid not in sibling_npc.relationships.siblings_uuids:
                    sibling_npc.relationships.add_sibling_link(self.owner_uuid)

    def get_parents_uuids(self) -> List[str]: return self.parents_uuids
    def get_children_uuids(self) -> List[str]: return self.children_uuids
    def get_siblings_uuids(self) -> List[str]: return self.siblings_uuids

    # --- Metodi per relazioni sociali/romantiche ---
    def set_romantic_partner(self, target_npc_uuid: str, is_partner: bool, game_state: 'GameState'):
        """Imposta o rimuove un partner romantico stabile."""
        if target_npc_uuid == self.owner_uuid: return
        rel_with_target = self._ensure_relationship_with(target_npc_uuid)
        if rel_with_target:
            rel_with_target.are_romantic_partners = is_partner
            # Aggiorna anche il partner
            target_npc = game_state.get_npc_by_uuid(target_npc_uuid)
            if target_npc and target_npc.relationships:
                rel_target_with_owner = target_npc.relationships._ensure_relationship_with(self.owner_uuid)
                if rel_target_with_owner:
                    rel_target_with_owner.are_romantic_partners = is_partner
            status = "partner" if is_partner else "non più partner"
            logger.info(f"Rel ({self.owner_name}): {target_npc_uuid[-6:]} è ora {status}.")


    def update(self, game_hours_advanced: float, game_state: 'GameState'):
        if game_hours_advanced <= 0: return
        decay_rate_friendship = getattr(config, 'REL_FRIENDSHIP_DECAY_PER_DAY', 0.05) / config.GAME_HOURS_IN_DAY
        decay_rate_romance = getattr(config, 'REL_ROMANCE_DECAY_PER_DAY', 0.1) / config.GAME_HOURS_IN_DAY
        decay_threshold_hours = getattr(config, 'REL_DECAY_INACTIVITY_THRESHOLD_HOURS', 24 * 2) # 2 giorni di gioco

        current_sim_hours = game_state.current_game_total_sim_hours_elapsed

        for target_uuid, rel in list(self.relationships.items()):
            rel.days_known_ingame += game_hours_advanced / config.GAME_HOURS_IN_DAY
            
            # Decadimento se non ci sono state interazioni recenti
            if current_sim_hours - rel.last_significant_interaction_time > decay_threshold_hours:
                if rel.friendship_level > 0 and decay_rate_friendship > 0:
                    rel.modify_friendship(-(decay_rate_friendship * game_hours_advanced), "Decadimento per inattività")
                elif rel.friendship_level < 0 and decay_rate_friendship > 0: # Tendenza verso la neutralità anche per inimicizia
                    rel.modify_friendship( (decay_rate_friendship * game_hours_advanced * 0.5), "Decadimento inimicizia")

                if rel.romance_level > 0 and decay_rate_romance > 0:
                    rel.modify_romance(-(decay_rate_romance * game_hours_advanced), "Decadimento per inattività")
                # Non far decadere il romance negativo verso la neutralità automaticamente,
                # a meno che non sia desiderato.

    def to_dict(self) -> Dict[str, Any]:
        rels_data = {uuid: rel.to_dict() for uuid, rel in self.relationships.items()}
        return {
            "relationships_map": rels_data, # Cambiato nome chiave per chiarezza
            "parents_uuids": self.parents_uuids,
            "children_uuids": self.children_uuids,
            "siblings_uuids": self.siblings_uuids,
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]], character_owner: 'Character', owner_uuid: str) -> 'RelationshipComponent':
        instance = cls(character_owner, owner_uuid)
        if data:
            rels_map_saved = data.get("relationships_map", {})
            for target_uuid, rel_data in rels_map_saved.items():
                if isinstance(rel_data, dict):
                    relationship_obj = Relationship.from_dict(rel_data)
                    if relationship_obj:
                        instance.relationships[target_uuid] = relationship_obj
            
            instance.parents_uuids = data.get("parents_uuids", [])
            instance.children_uuids = data.get("children_uuids", [])
            instance.siblings_uuids = data.get("siblings_uuids", [])
        
        if DEBUG_RELATIONSHIP and data:
            logger.debug(f"RelationshipComponent per {character_owner.name} caricato con {len(instance.relationships)} relazioni dirette e {len(instance.parents_uuids)} genitori.")
        return instance