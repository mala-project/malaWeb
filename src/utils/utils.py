import json
from typing import Tuple

import ase
import pandas as pd


def ase_to_df(atoms_object: ase.atoms) -> pd.DataFrame:
    atoms = [[], [], [], [], []]
    for i in range(0, len(atoms_object)):
        atoms[0].append(atoms_object[i].symbol)
        atoms[1].append(atoms_object[i].charge)
        atoms[2].append(atoms_object.get_positions()[i, 0])
        atoms[3].append(atoms_object.get_positions()[i, 1])
        atoms[4].append(atoms_object.get_positions()[i, 2])
    return pd.DataFrame(
        data={
            "x": atoms[2],
            "y": atoms[3],
            "z": atoms[4],
            "ordinal": atoms[0],
            "charge": atoms[1],
        }
    )


def get_config() -> Tuple[int, list]:
    """
    Getter for malaWeb's config, containing
        atom_limit: Int
            a threshold for no. of Atoms in ase.Atoms that would cause high computational time of inference.
            mW displays a warning if surpassed.
        models: List[dict]
            A list of entries that specify the available Training data. An entry consists of:
                "label" is the label visible in the apps dropdown
                "value"  is the value passed to the inference script. Consists of model identifier|temperature.
                -> Ranges of temperature are to be surrounded by []
    """
    config = json.load(open("../src/config.json", "r"))
    atom_limit = config["atom_limit"]
    models = [{'label': model['label'], 'value': model['value'], 'path': model['path']} for model in config["models"]]
    return atom_limit, models
