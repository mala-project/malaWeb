# malaWeb
Web app to visualize on-the-fly MALA predictions. 

# Description
malaWeb is a Plotly Dash based web application used for the visualization of 3D volumetric data.
By inputting atom positions and cell information in ASE-accepted data formats, MALA can be run to make predictions on the volumetric data inside the given cell.
It is currently made to be run on a local machine with its own MALA installation. Be aware that larger model predictions will take a lot of time.

# Installation
Running a MALA inference requires a working installation of MALA and its dependencies (torch, LAMMPS, QuantumEspresso, ..), as well as model data.
See https://github.com/mala-project/mala/blob/develop/docs/source/install/installing_mala.rst on how to install.
The model data is currently included in this malaWeb repository, stored in "models"-folder and listed in "model_list.json".
It is recommended to install MALA in an anaconda virtual environment.

After MALA is installed, just run the setup.py file to install malaWebs dependencies.
- In directory with setup.py, run "pip install -e ."


Make sure the installed version of the dash uploader component is the newest pre-release version 0.7.0 or newer, as this introduces new syntax.
https://github.com/fohrloop/dash-uploader#-dash-uploader-070-pre-release-available

Make sure the installed version of packaging is not higher than 21. For a version check, the dash uploader component uses an attribute "LegacyVersion" that has been deprecated in later versions.
See this thread: https://github.com/pypa/packaging/issues/321

# Usage
After installing dependencies, run app.py.
In the File-Upload section, upload an ASE-readable file (See: https://wiki.fysik.dtu.dk/ase/ase/io/io.html - Table - Formats with either R or RW capabilities).
The data read by ASE will be displayed in a popup window.
- A dropdown contains all uploaded atom positions
- The given cell is rendered with given atom positions inside
- A model has to be chosen for running the MALA inference. Some models support varying temperatures, so make sure to edit if necessary, before running (calculation heavy) predictions
- Run MALA

- The visualization will open up. The settings panel on the right hand side gives options for predefined camera angles, rendering options for the voxels and their size, opacity and outlines as well as atoms and cell boundaries.
The Tools panel just below the visualization lets you render layers in all 3 axis, as well as filter voxels by their density value.
Layer settings can quickly be en- and disabled by pressing the respective axis button and reset by pressing X to the sliders right.
The bottom of the page has a button for opening up information on different energies and a graph of the density of state.



# Todos
- Create an environment.yml, as the app will most likely be installed in conda venv
- Rework "edit" and "reset" button