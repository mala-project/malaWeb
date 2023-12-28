"""Script for single MALA inference."""
import json
import time

import mala
import numpy as np

# Set up the path to the model.
MODELS = json.load(open("../src/models/model_paths.json"))

model_paths = {
    "Be|298": "Be_model",
    "Al|298": None,
    "Al|933": None,
    "Al|[100,933]": None,
    "Debug|0": None,
}


def run_mala_prediction(atoms_to_predict, model_and_temp,
                        calc_total_energy=True):
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
    if model_and_temp["name"] == "Debug|0":
        print("Debug-Inf")

        params = mala.Parameters()
        ldos_calculator = mala.LDOS(params)
        ldos_calculator.read_additional_calculation_data(
            [atoms_to_predict, [20, 20, 20]]
        )

        results = {
            "band_energy": 123.0,
            "total_energy": 456.0,
            # Reshaping for plotting.
            "density": np.random.random([20, 20, 20]),
            "density_of_states": [0.0, 1.0, 2.0, 3.0, 4.0],
            "energy_grid": [0.0, 1.0, 2.0, 3.0, 4.0],
            "fermi_energy": 789.0,
            "voxel": ldos_calculator.voxel,
            "grid_dimensions": ldos_calculator.grid_dimensions,
        }
        print(results["voxel"])
        print(results["grid_dimensions"])
        return results
    else:
        parameters, network, data_handler, predictor = mala.Predictor.load_run(
            MODELS[model_and_temp["name"]], path="models"
        )
        predicted_ldos = predictor.predict_for_atoms(atoms_to_predict)

        ldos_calculator: mala.LDOS
        ldos_calculator = predictor.target_calculator
        ldos_calculator.read_from_array(predicted_ldos)

        results = {
            "band_energy": ldos_calculator.band_energy,
            # Reshaping for plotting.
            "density": np.reshape(
                ldos_calculator.density, ldos_calculator.grid_dimensions
            ),
            "density_of_states": ldos_calculator.density_of_states,
            "energy_grid": ldos_calculator.energy_grid,
            "fermi_energy": ldos_calculator.fermi_energy,
            "voxel": ldos_calculator.voxel,
            "grid_dimensions": ldos_calculator.grid_dimensions,
        }
        if calc_total_energy:
            results["total_energy"] = ldos_calculator.total_energy
        else:
            results["total_energy"] = 0.0
        return results


def save_density_to_file(results, file_name):
    """
    Save the density of an inference back to file.

    Function returns nothing, but writes a single file containing the density.

    Parameters
    ----------
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

    file_name : string
        Name of the file in which the density will be saved.
    """
    parameters = mala.Parameters()
    density_calculator = mala.Density(parameters)
    density_calculator.voxel = results["voxel"]
    density_calculator.atoms = results["atoms"]
    density_calculator.density = results["density"]
    density_calculator.grid_dimensions = results["grid_dimensions"]
    density_calculator.write_to_cube(file_name)


def save_dos_to_file(results, dos_file_name, energy_grid_file_name):
    """
    Save the density of an inference back to file.

    Function returns nothing, but writes two numpy files,
    containing DOS and energy grid.

    Parameters
    ----------
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

    dos_file_name : string
        Name of the file in which the DOS will be saved.

    energy_grid_file_name : string
        Name of the file in which the energy grid will be saved.
    """

    parameters = mala.Parameters()
    dos_calculator = mala.DOS(parameters)
    # A bit hacky, the general write function will be used for
    # both the actual DOS as well as the energy grid.
    dos_calculator.density_of_states = results["density_of_states"]
    dos_calculator.write_to_numpy_file(dos_file_name)
    dos_calculator.density_of_states = results["energy_grid"]
    dos_calculator.write_to_numpy_file(energy_grid_file_name)


