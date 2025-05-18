# game/src/ai/actions/__init__.py

# Importa i moduli delle azioni per renderli disponibili
# come un pacchetto (opzionale, ma può semplificare gli import altrove)

from . import idle
from . import resting_on_bed
from . import seeking_bed
from . import phoning
from . import romantic_interaction # Conterrà logica per interazioni e attesa
from . import going_to_bed_together # Conterrà logica per leader e follower
from . import cuddling_in_bed
from . import wandering
from . import using_toilet
# Aggiungi altri moduli di azione qui quando li crei (es. eating_food)

# Potresti anche definire un dizionario di handler qui,
# anche se l'abbiamo definito in npc_behavior.py per ora.
# Se lo definisci qui, npc_behavior.py potrebbe importarlo da qui.
# Esempio:
# ACTION_UPDATE_HANDLERS = {
#     "resting_on_bed": resting_on_bed.update_resting_on_bed,
#     "phoning": phoning.update_phoning,
#     "cuddling_in_bed": cuddling_in_bed.update_cuddling_in_bed,
#     "romantic_interaction_action": romantic_interaction.update_romantic_interaction,
#     "affectionate_interaction_action": romantic_interaction.update_affectionate_interaction,
#     "accepting_intimacy_and_waiting": romantic_interaction.update_accepting_intimacy_and_waiting,
#     "going_to_bed_together_leader": going_to_bed_together.update_going_to_bed_leader,
#     "going_to_bed_together_follower": going_to_bed_together.update_going_to_bed_follower,
#     "post_intimacy_idle": idle.update_post_interaction_idle,
#     "using_toilet": using_toilet.update_using_toilet,
#     # Azioni di "seeking" e "wandering" sono più guidate dal pathfinding,
#     # quindi il loro "update" è il movimento stesso, gestito in Character.py.
#     # La loro logica di "inizio" e "arrivo" sarà in moduli dedicati.
# }

# ACTION_ARRIVAL_HANDLERS = {
#     "seeking_bed": seeking_bed.handle_arrival_at_bed,
#     "seeking_partner_for_intimacy": romantic_interaction.handle_arrival_at_partner_for_intimacy, # Spostato qui
#     "going_to_bed_together_leader": going_to_bed_together.handle_arrival_at_bed_leader,
#     "going_to_bed_together_follower": going_to_bed_together.handle_arrival_at_bed_follower,
#     "seeking_toilet": using_toilet.handle_arrival_at_toilet,
#     "wandering": wandering.handle_arrival_at_wander_destination,
# }

# ACTION_DECISION_LOGIC = {
#     "idle": idle.handle_idle_decision,
# }

# Questo modo di organizzare gli handler potrebbe essere più pulito se npc_behavior.py
# importa questi dizionari direttamente da actions.