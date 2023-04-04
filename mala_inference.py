"""Script for single MALA inference."""

import mala
import numpy as np

# Set up the path to the model.
model_paths = {
    "Be|298": "Be_model",
    "Al|298": None,
    "Al|933": None,
    "Al|[100,933]": None,
}


def run_mala_prediction(atoms_to_predict, model_and_temp):
    """
    Perform a MALA prediction for an ase.Atoms object.

    Parameters
    ----------
    atoms_to_predict : ase.Atoms
        Atoms for which to perform the prediction.

    model_and_temp : dict
        A dictionary containing the name of the model to use and the
        temperature at which to run inference on.

    Returns
    -------
    results : dict
        A dictionary that contains:
            "band_energy": The band energy, which can be useful for specific
                           analysis.

            "total_energy": The total energy of the system, which is the
                            principal quantity to investigate when e.g.
                            optimizing the atomic geometry of a system.

            "density": Electronic density as a 3D numpy array, which
                       gives information about the electronic distribution.

            "density_of_states": The density of states (DOS) which is an
                                 important property in analyzing electrical
                                 and optical phenomena.

            "energy_grid": The energy grid on which the DOS is supposed
                           to be plotted.
    """
    parameters, network, data_handler, predictor = mala.Predictor.load_run(
        model_paths[model_and_temp["name"]], path="./models")
    predicted_ldos = predictor.predict_for_atoms(atoms_to_predict)

    ldos_calculator = predictor.target_calculator
    ldos_calculator.read_from_array(predicted_ldos)

    results = {
        "band_energy": ldos_calculator.band_energy,
        "total_energy": ldos_calculator.total_energy,
        "density": ldos_calculator.density,
        "density_of_states": ldos_calculator.density_of_states,
        "energy_grid": ldos_calculator.energy_grid,
    }

    return results
