# malaWeb
Web app to visualize on-the-fly MALA predictions. 

Note: So far, this only renders test-data for BE2. NOT the data that is uploaded. 
There is only a file-format-check for ASE-readability happening. If successful, a hardcoded inference-script is run.
The atoms listed in the upload-popup are read from file though.

# Installation:

- MALA needs to be installed together with Lammps
- When using Anaconda for MALA:
  - conda install -c conda-forge dash
  - conda install -c conda-forge dash-bootstrap-components
  - pip install dash-uploader --pre

# Usage:
- run app.py