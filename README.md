# malaWeb
Web app to visualize on-the-fly MALA predictions. 

Note: So far, this only renders test-data for BE2. NOT the data that is uploaded. 
There is only a type-check for .cube happening. If successfull, a hardcoded inference-script is run.

# Installation:

- MALA needs to be installed together with Lammps
- When using Anaconda for MALA:
  - conda install -c conda-forge dash
  - conda install -c conda-forge dash-bootstrap-components

# Usage:
- run app.py