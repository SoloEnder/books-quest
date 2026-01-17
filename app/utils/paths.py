
# app/base_path.py
from pathlib import Path
import sys

# Oui, ce code à été fait par une IA T T

def get_base_path() -> Path:
    """
    Retourne le répertoire racine du projet, quel que soit le contexte
    d'exécution (script normal, PyInstaller --onedir ou --onefile).

    - En mode PyInstaller, le répertoire contenant le sous‑dossier `_internal`
      est la racine souhaitée.
    - En mode développement, on remonte simplement jusqu'à la première
      occurrence de `_internal` (au cas où le projet serait déjà structuré
      ainsi) ou on utilise une profondeur fixe comme secours.
    """
    # ------------------------------------------------------------------
    # Cas où le binaire a été créé par PyInstaller (frozen)
    # ------------------------------------------------------------------
    if getattr(sys, "frozen", False):
        # sys._MEIPASS pointe vers le répertoire temporaire où PyInstaller
        # a extrait les fichiers. Dans le mode --onedir il contient
        # le sous‑dossier `_internal`. Dans le mode --onefile il ne le
        # contient pas, mais le répertoire même est la racine.
        start = Path(sys._MEIPASS).resolve()
    else:
        # ----------------------------------------------------------------
        # Cas normal (exécution depuis le code source)
        # ----------------------------------------------------------------
        start = Path(__file__).resolve()

    # --------------------------------------------------------------------
    # Parcourir les parents à la recherche de `_internal`
    # --------------------------------------------------------------------
    for current in start.parents:
        internal_dir = current / "_internal"
        if internal_dir.is_dir():
            # Le répertoire qui contient `_internal` est la racine du projet
            return current

    # --------------------------------------------------------------------
    # Aucun `_internal` trouvé → on utilise une profondeur fixe.
    # Ici on suppose que le projet a la forme :
    #   project/
    #   ├─ app/
    #   │   └─ base_path.py   <-- ce fichier
    #   └─ data/ …
    # => on remonte de 2 niveaux (app → project)
    # Ajustez le nombre si votre arborescence diffère.
    # --------------------------------------------------------------------
    try:
        return start.parents[2]          # 0 = fichier, 1 = app/, 2 = project/
    except IndexError:
        # Si la profondeur n’est pas suffisante, on renvoie simplement le
        # répertoire du fichier lui‑même (fallback très sûr).
        return start.parent
    
def get_abspath(path: str):
    base_path = get_base_path()
    final_path = base_path.joinpath(path)
    return final_path.absolute()
