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