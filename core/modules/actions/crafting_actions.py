# core/modules/actions/crafting_actions.py
import random
import uuid

from core.enums.object_types import ObjectType
from .action_base import BaseAction
from core.enums import ActionType, SkillType, ItemQuality
from core.world.game_object import GameObject
from core import settings

class CookAction(BaseAction):
    """Azione per cucinare un pasto. L'esito è un oggetto 'cibo' con una qualità."""
    
    def on_finish(self):
        super().on_finish()
        if not self.npc: return

        # 1. Determina la qualità del pasto in base alla skill COOKING
        skill_level = self.npc.skill_manager.get_skill_level(SkillType.COOKING)
        
        # Esempio di logica: più alta la skill, più alta la probabilità di un buon pasto
        #                  pesi: [scadente, normale, buono, eccellente, capolavoro]
        weights = [10, 60, 20, 10, 0] # Default per livello basso
        if skill_level > 3: weights = [5, 45, 35, 15, 2]
        if skill_level > 7: weights = [0, 10, 40, 40, 10]
        
        food_quality = random.choices(list(ItemQuality), weights=weights, k=1)[0]

        # 2. Crea il nuovo oggetto "Pasto"
        # In futuro, questo oggetto potrebbe essere aggiunto all'inventario dell'NPC
        # o posizionato su una superficie. Per ora, lo passiamo direttamente a EatAction.
        food_object = GameObject(
            object_id=f"food_{uuid.uuid4().hex[:6]}", name=f"Pasto ({food_quality.name})",
            object_type=ObjectType.FOOD, quality=food_quality
        )

        if settings.DEBUG_MODE:
            print(f"    [CookAction] {self.npc.name} ha cucinato un pasto di qualità: {food_quality.name}")
        
        # 3. Accoda l'azione di mangiare il pasto appena creato
        # Qui dovremmo creare una EatAction specifica che prende l'oggetto cibo
        # Per ora, semplifichiamo e immaginiamo che l'NPC mangi subito.