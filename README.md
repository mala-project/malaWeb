# malaWeb (for local hosting)

Web app to visualize on-the-fly MALA predictions.

## Description

malaWeb is a Plotly Dash based web application used for the visualization of 3D volumetric data. By inputting atom positions and cell information in ASE-accepted data formats, MALA can be run to make predictions on the volumetric data inside the given cell. It is currently made to be run on a local machine with its own MALA installation. Be aware that larger model predictions will take a lot of time. The default atom limit for predictions is 200.

## Installation

Running a MALA inference requires a working installation of MALA and its dependencies (torch, LAMMPS, QuantumEspresso, ..), as well as model data.\
See https://github.com/mala-project/mala/blob/develop/docs/source/install/installing\_mala.rst on how to install.\
Some model data is currently included in this malaWeb repository, stored in "models"-folder and listed in "model\_list.json". It is recommended to install MALA in an anaconda virtual environment.

After MALA is installed, just run the setup.py file to install malaWebs dependencies.

* In directory with setup.py, run `pip install -e .`

Make sure the installed version of the dash uploader component is the newest pre-release version 0.7.0 or newer, as this introduces new syntax. https://github.com/fohrloop/dash-uploader#-dash-uploader-070-pre-release-available

Make sure the installed version of packaging is not higher than 21. For a version check, the dash uploader component uses an attribute "LegacyVersion" that has been deprecated in later versions. See this thread: https://github.com/pypa/packaging/issues/321

## Usage

After installing dependencies, run app.py.\
The app will be accessible locally under http://0.0.0.0:8050/. This can be changed at the very end of app.py.

\
In the File-Upload section, upload an ASE-readable file\
(See: https://wiki.fysik.dtu.dk/ase/ase/io/io.html -> Table -> Formats with either R or RW capabilities).\
The data read by ASE will be displayed in a popup window for running an Inference

<figure><img src="assets/images/inference-popup.png" alt=""><figcaption><p>Inference popup</p></figcaption></figure>

* A dropdown lists all uploaded atom positions
* The given cell is rendered with given atom positions inside
* A model has to be chosen for running the MALA inference. Some models support varying temperatures, so make sure to edit if necessary, before running (calculation heavy) predictions
* Run MALA



<figure><img src="assets/images/webapp-overview.png" alt=""><figcaption><p>Overview of malaWeb</p></figcaption></figure>

* (1) The interactive visualization will open up.
* (2) The Sidebar to the left contains:
  * Upload section
  * The edit button for opening up the Inference pop up again, to enable running another inference (f.e. same data, different model)
  * The reset button to delete the uploaded data and reset the visualization
* (3) The Settings panel on the right hand side gives options for:
  * &#x20;Predefined camera angles
  * Rendering options for the 'voxels' and their size, opacity and outlines as well as atoms and cell boundaries.
* (4) The Tools panel just below the visualization lets you render layers in all 3 axis, as well as filter voxels by their density value. Layer settings can quickly be en- and disabled by pressing the respective axis button and reset by pressing X to the sliders right.
* (5) The bottom of the page has a button for opening up information on different energies and a graph of the density of state.

## Todos

Goals for V1 are:

* Rework "edit" and "reset" button

Goals for V1.1 are:

* Implement a different visualization (opposed to plotlys 3D scatter plot) like CrystalToolkit (https://github.com/materialsproject/crystaltoolkit). Scatterplots have their limits f.e. in accuracy (not voxel) and performance of big datasets
* Optimize Dash callbacks --> f.e. further implement the newly introduced patch-methods
* Reduce Panda Dataframe iterations f.e. in Plot-Slicing --> better DF filtering
* (Maybe) For the setup: Create an environment.yml, as the app will most likely be installed in a conda env
* Prepare the app for hosting, possibly with HPC-capabilities
* General overhaul according to concept
