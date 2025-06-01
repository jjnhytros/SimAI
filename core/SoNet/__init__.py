# core/__init__.py

# Questo file rende la cartella 'core' un package Python.
# Può essere usato per esporre interfacce pubbliche del package
# o per eseguire codice di inizializzazione specifico del package.

# Aggiungiamo un print per vedere quando il package viene caricato.
print("Package 'core' caricato.")

# In futuro, potremmo importare qui le classi principali dai moduli di 'core'
# per renderle più facilmente accessibili dall'esterno. Ad esempio:
#
# from .simulation import Simulation
# from .character import Character
#
# Questo permetterebbe di fare `from core import Simulation` in simai.py
# invece di `from core.simulation import Simulation`.
# Per ora, lo lasciamo semplice.