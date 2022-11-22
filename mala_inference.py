"""Script for single MALA inference."""

import mala
import numpy as np

# Set up the path to the model.
Be2_parameters_path = "/home/maxyyy/PycharmProjects/mala/app/script/Be2_model.params.json"
Be2_weights_path = "/home/maxyyy/PycharmProjects/mala/app/script/Be2_model.network.pth"
Be2_iscaler_path = "/home/maxyyy/PycharmProjects/mala/app/script/Be2_model.iscaler.pkl"
Be2_oscaler_path = "/home/maxyyy/PycharmProjects/mala/app/script/Be2_model.oscaler.pkl"


def run_mala_prediction(atoms_to_predict, parameters_path,
                        weights_path, iscaler_path, oscaler_path,
                        number_of_electrons_per_atom=4, temperature=298,
                        save_density_cube_as=None):
    """
    Perform a MALA prediction for an ase.Atoms object.

    Parameters
    ----------
    atoms_to_predict : ase.Atoms
        Atoms for which to perform the prediction.

    parameters_path : string
        Path to the parameters.json file for MALA.

    weights_path : string
        Path to the parameters.json file for MALA.

    iscaler_path : string
        Path to the file containing the NN weights.

    oscaler_path : string
        Path to the file containing the output scaler coefficients.

    number_of_electrons_per_atom : int
        Path to the parameters.json file for MALA.

    temperature : float
        Path to the parameters.json file for MALA.

    save_density_cube_as : string
        When not None, the density will also be saved to this file.

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
    new_parameters = mala.Parameters.load_from_file(parameters_path)
    new_parameters.targets.target_type = "LDOS"
    new_parameters.targets.ldos_gridsize = 11
    new_parameters.targets.ldos_gridspacing_ev = 2.5
    new_parameters.targets.ldos_gridoffset_ev = -5
    new_parameters.running.inference_data_grid = [18, 18, 27]

    new_parameters.descriptors.descriptor_type = "SNAP"
    new_parameters.descriptors.twojmax = 10
    new_parameters.descriptors.rcutfac = 4.67637
    new_parameters.descriptors.lammps_compute_file = "/home/maxyyy/PycharmProjects/mala/mala/descriptors/in.bgrid.python"
    iscaler = mala.DataScaler.load_from_file(iscaler_path)
    oscaler = mala.DataScaler.load_from_file(oscaler_path)

    inference_data_handler = mala.DataHandler(new_parameters,
                                              input_data_scaler=iscaler,
                                              output_data_scaler=oscaler)

    new_network = mala.Network.load_from_file(new_parameters, weights_path)
    predictor = mala.Predictor(new_parameters, new_network,
                               inference_data_handler)

    ldos = predictor.predict_for_atoms(atoms_to_predict)
    ldos_calculator: mala.LDOS = inference_data_handler.target_calculator

    ldos_calculator.number_of_electrons = number_of_electrons_per_atom
    ldos_calculator.temperature_K = temperature

    fermi_energy = ldos_calculator.get_self_consistent_fermi_energy_ev(ldos)

    band_energy = ldos_calculator. \
        get_band_energy(ldos, fermi_energy_eV=fermi_energy)

    # TODO: Get full total energy.
    total_energy = 0.0
    density = ldos_calculator.get_density(ldos, fermi_energy_ev=fermi_energy)
    density = np.reshape(density, new_parameters.running.inference_data_grid)
    if save_density_cube_as is not None:
        density_calculator = mala.Density.from_ldos(ldos_calculator)
        density_calculator.write_as_cube(save_density_cube_as, density)

    density_of_states = ldos_calculator.get_density_of_states(ldos)
    energy_grid = ldos_calculator.get_energy_grid()

    results = {
        "band_energy": band_energy,
        "total_energy": total_energy,
        "density": density,
        "density_of_states": density_of_states,
        "energy_grid": energy_grid,
    }
    return results

# For testing.
from ase.io import read
atoms = read("/home/maxyyy/PycharmProjects/examples/Be2/training_data/"
             "Be_snapshot1.out")

# Actually run the prediction.
results = run_mala_prediction(atoms, Be2_parameters_path, Be2_weights_path,
                              Be2_iscaler_path, Be2_oscaler_path,
                              save_density_cube_as="Be2_density.cube")