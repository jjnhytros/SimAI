# game/src/entities/components/inventory_component.py
import logging
from typing import Dict, Any, Optional, List, TYPE_CHECKING, Union, Tuple # <-- 'Tuple' AGGIUNTO QUI

# Importa dal package 'game'
from game import config
# Importa la classe Item (assicurati che il percorso sia corretto)
# Se items.py è in entities, l'import è: from ..items import Item 
# Se items.py è in entities/components, l'import è: from .items import Item
# Questo percorso presuppone che items.py sia in game/src/entities/
from game.src.entities.items import Item 

if TYPE_CHECKING:
    from game.src.entities.character import Character # Per il type hint di character_owner

logger = logging.getLogger(__name__)
DEBUG_INVENTORY = getattr(config, 'DEBUG_AI_ACTIVE', False)

class InventorySlot:
    """Rappresenta uno slot dell'inventario che può contenere un tipo di Item e una quantità."""
    def __init__(self, item: Optional[Item] = None, quantity: int = 0):
        self.item: Optional[Item] = None
        self.quantity: int = 0
        if item:
            self.item = item # Assegna l'istanza Item
            self.quantity = quantity
            if not item.stackable and quantity > 1:
                logger.warning(f"Tentativo di creare InventorySlot con quantity > 1 per item non stackable: {item.name}")
                self.quantity = 1
        
    def can_add(self, item_to_add: Item, quantity_to_add: int = 1) -> int:
        """Verifica quanti di item_to_add possono essere aggiunti a questo slot."""
        if not self.item: # Slot vuoto
            return min(quantity_to_add, item_to_add.max_stack if item_to_add.stackable else 1)
        if self.item.item_id == item_to_add.item_id and self.item.stackable:
            can_fit = self.item.max_stack - self.quantity
            return min(quantity_to_add, can_fit)
        return 0 

    def add_item_instance(self, item_instance_to_add: Item, quantity_to_add: int = 1) -> int:
        """Aggiunge una specifica istanza di Item (o quantità di essa) a questo slot. 
           Restituisce la quantità non aggiunta.
        """
        if quantity_to_add <= 0: return 0

        if not self.item: # Slot vuoto
            self.item = item_instance_to_add 
            can_take = self.item.max_stack if self.item.stackable else 1
            actual_added = min(quantity_to_add, can_take)
            self.quantity = actual_added
            return quantity_to_add - actual_added
        
        if self.item.item_id == item_instance_to_add.item_id and self.item.stackable:
            can_take_more = self.item.max_stack - self.quantity
            actual_added = min(quantity_to_add, can_take_more)
            self.quantity += actual_added
            return quantity_to_add - actual_added
        
        return quantity_to_add

    def remove_quantity(self, quantity_to_remove: int = 1) -> Tuple[Optional[Item], int]: # Ora Tuple è definito
        """
        Rimuove una quantità di item da questo slot.
        Restituisce l'item template e la quantità effettivamente rimossa.
        Se lo slot si svuota, self.item diventa None.
        """
        if not self.item or self.quantity == 0 or quantity_to_remove <= 0:
            return None, 0
        
        item_template_removed = self.item
        actual_removed = min(quantity_to_remove, self.quantity)
        self.quantity -= actual_removed
        
        if self.quantity == 0:
            self.item = None
        return item_template_removed, actual_removed

    def is_empty(self) -> bool:
        return self.item is None or self.quantity == 0

    def get_item_id(self) -> Optional[str]:
        return self.item.item_id if self.item else None

    def to_dict(self) -> Optional[Dict[str, Any]]:
        if self.item:
            return {
                "item_data": self.item.to_dict(), 
                "quantity": self.quantity
            }
        return None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InventorySlot':
        item_data = data.get("item_data")
        item_obj = Item.from_dict(item_data) if item_data else None
        return cls(item=item_obj, quantity=data.get("quantity", 0))


class InventoryComponent:
    def __init__(self, 
                 character_owner: Optional['Character'], 
                 capacity: int = getattr(config, 'NPC_INVENTORY_CAPACITY', 10),
                 owner_name_for_log: Optional[str] = None):
        self.owner: Optional['Character'] = character_owner
        if character_owner: self.owner_name: str = character_owner.name
        elif owner_name_for_log: self.owner_name: str = owner_name_for_log
        else: self.owner_name: str = "Inventario Sconosciuto"
        
        self.capacity: int = capacity
        self.slots: List[InventorySlot] = [InventorySlot() for _ in range(capacity)]

        if DEBUG_INVENTORY:
            logger.debug(f"InventoryComponent per '{self.owner_name}' inizializzato con {self.capacity} slot.")

    def add_item_instance(self, item_instance_to_add: Item, quantity_to_add: int = 1) -> bool:
        if not isinstance(item_instance_to_add, Item):
            logger.error(f"Inventory ('{self.owner_name}'): Tentativo di aggiungere oggetto non Item: {item_instance_to_add}")
            return False
        if quantity_to_add <= 0: return True

        remaining_quantity_to_add = quantity_to_add

        if item_instance_to_add.stackable:
            for slot in self.slots:
                if not slot.is_empty() and slot.item and slot.item.item_id == item_instance_to_add.item_id: # Aggiunto slot.item
                    can_add_here = slot.can_add(item_instance_to_add, remaining_quantity_to_add)
                    if can_add_here > 0:
                        not_added = slot.add_item_instance(item_instance_to_add, can_add_here)
                        if not_added != 0: 
                             logger.error(f"Inventory ('{self.owner_name}'): slot.add_item_instance ha restituito un valore inatteso {not_added}")
                        remaining_quantity_to_add -= (can_add_here - not_added)
                    if remaining_quantity_to_add == 0: break
            if remaining_quantity_to_add == 0:
                if DEBUG_INVENTORY: logger.debug(f"Inventory ('{self.owner_name}'): Aggiunte {quantity_to_add} x '{item_instance_to_add.name}' a stack esistente.")
                return True

        if remaining_quantity_to_add > 0:
            for slot in self.slots:
                if slot.is_empty():
                    can_add_here = slot.can_add(item_instance_to_add, remaining_quantity_to_add)
                    if can_add_here > 0:
                        not_added = slot.add_item_instance(item_instance_to_add, can_add_here)
                        if not_added != 0:
                             logger.error(f"Inventory ('{self.owner_name}'): slot.add_item_instance (slot vuoto) ha restituito un valore inatteso {not_added}")
                        remaining_quantity_to_add -= (can_add_here - not_added)
                    if remaining_quantity_to_add == 0: break
            if remaining_quantity_to_add == 0:
                if DEBUG_INVENTORY: logger.debug(f"Inventory ('{self.owner_name}'): Aggiunte {quantity_to_add} x '{item_instance_to_add.name}' in slot nuovi.")
                return True
        
        if remaining_quantity_to_add > 0:
            logger.warning(f"Inventory ('{self.owner_name}'): Inventario pieno o item non stackabile. Impossibile aggiungere {remaining_quantity_to_add} x '{item_instance_to_add.name}'.")
            return False
        return True

    def remove_item_by_id(self, item_id_to_remove: str, quantity_to_remove: int = 1) -> int:
        if quantity_to_remove <= 0: return 0
        total_removed_count = 0; remaining_to_remove_this_call = quantity_to_remove
        for slot in reversed(self.slots):
            if not slot.is_empty() and slot.item and slot.item.item_id == item_id_to_remove: # Aggiunto slot.item
                _item_template, removed_from_this_slot = slot.remove_quantity(remaining_to_remove_this_call)
                total_removed_count += removed_from_this_slot
                remaining_to_remove_this_call -= removed_from_this_slot
                if remaining_to_remove_this_call == 0: break
        if DEBUG_INVENTORY and total_removed_count > 0: logger.debug(f"Inventory ('{self.owner_name}'): Rimossi {total_removed_count} x '{item_id_to_remove}'.")
        elif total_removed_count < quantity_to_remove: logger.warning(f"Inventory ('{self.owner_name}'): Richiesto di rimuovere {quantity_to_remove} x '{item_id_to_remove}', ma rimossi solo {total_removed_count}.")
        return total_removed_count

    def has_item_id(self, item_id: str, quantity: int = 1) -> bool:
        count = 0
        for slot in self.slots:
            if not slot.is_empty() and slot.item and slot.item.item_id == item_id: # Aggiunto slot.item
                count += slot.quantity
                if count >= quantity: return True
        return False

    def get_item_count_by_id(self, item_id: str) -> int:
        count = 0
        for slot in self.slots:
            if not slot.is_empty() and slot.item and slot.item.item_id == item_id: # Aggiunto slot.item
                count += slot.quantity
        return count
    
    def get_all_slots(self) -> List[InventorySlot]:
        return self.slots
        
    def get_filled_slots_info(self) -> List[Dict[str, Any]]:
        info_list = []
        for slot in self.slots:
            if not slot.is_empty() and slot.item: # Aggiunto slot.item
                info_list.append({
                    "name": slot.item.name, "item_id": slot.item.item_id, "quantity": slot.quantity,
                    "description": slot.item.description, "stackable": slot.item.stackable,
                    "max_stack": slot.item.max_stack, "properties": slot.item.properties
                })
        return info_list

    def update(self, game_hours_advanced: float, game_state_ref: 'GameState'):
        pass # Logica futura per deterioramento, ecc.

    def to_dict(self) -> Dict[str, Any]:
        serialized_slots = [slot.to_dict() for slot in self.slots if not slot.is_empty()]
        return {"capacity": self.capacity, "filled_slots_data": serialized_slots}

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]], 
                  character_owner: Optional['Character'],
                  owner_name_for_log: Optional[str] = None) -> 'InventoryComponent':
        capacity = getattr(config, 'NPC_INVENTORY_CAPACITY', 10)
        if data and "capacity" in data: capacity = int(data["capacity"])
        log_name = (character_owner.name if character_owner else owner_name_for_log if owner_name_for_log else "Inventario Caricato")
            
        instance = cls(character_owner, capacity=capacity, owner_name_for_log=log_name if not character_owner else None)
        if data and "filled_slots_data" in data:
            filled_slots_data = data["filled_slots_data"]
            for i, slot_data in enumerate(filled_slots_data):
                if i < instance.capacity and slot_data is not None:
                    try: instance.slots[i] = InventorySlot.from_dict(slot_data)
                    except Exception as e: logger.error(f"Inventory ('{instance.owner_name}'): Errore caricamento slot {i}: {e}")
        if DEBUG_INVENTORY and data:
            filled_count = sum(1 for slot in instance.slots if not slot.is_empty())
            logger.debug(f"InventoryComponent per '{instance.owner_name}' caricato: {filled_count}/{instance.capacity} slot.")
        return instance