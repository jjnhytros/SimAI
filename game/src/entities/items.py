# game/src/entities/items.py
import uuid
from typing import Dict, Any, Optional

class Item:
    def __init__(self, item_id: str, name: str, description: str = "", 
                 stackable: bool = False, max_stack: int = 1,
                 properties: Optional[Dict[str, Any]] = None):
        self.item_id = item_id
        self.instance_uuid = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.stackable = stackable
        self.max_stack = max_stack if stackable else 1
        self.properties = properties if properties else {}

    def to_dict(self) -> Dict[str, Any]:
        # Semplificato, in realtà caricheresti da blueprint usando item_id
        return { "item_id": self.item_id, "name": self.name, "quantity": 1, 
                   "description": self.description, "stackable": self.stackable, 
                   "max_stack": self.max_stack, "properties": self.properties,
                   "instance_uuid": self.instance_uuid}


    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Item':
        # In un sistema reale, caricheresti il blueprint dell'item da item_id
        # e poi applicheresti le proprietà specifiche dell'istanza.
        item = cls(
            item_id=data["item_id"],
            name=data.get("name", data["item_id"]),
            description=data.get("description", ""),
            stackable=data.get("stackable", False),
            max_stack=data.get("max_stack", 1),
            properties=data.get("properties", {})
        )
        item.instance_uuid = data.get("instance_uuid", str(uuid.uuid4())) # Ripristina o genera nuovo
        return item

# Potresti voler spostare ITEM_BLUEPRINTS e create_item qui o in un item_manager