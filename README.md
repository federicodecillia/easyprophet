# easyprophet: Simplified Automatic Forecasting Procedure
[![Pypi_Version](https://img.shields.io/pypi/v/easyprophet.svg)](https://pypi.python.org/pypi/easyprophet)
[![GitHub license](https://img.shields.io/github/license/federicodecillia/easyprophet)](https://github.com/federicodecillia/easyprophet/blob/main/LICENSE)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v2.0%20adopted-ff69b4.svg)](code_of_conduct.md)
[![Build Status](https://travis-ci.com/federicodecillia/easyprophet.svg?branch=main)](https://travis-ci.com/federicodecillia/easyprophet)
[![Coverage Status](https://coveralls.io/repos/github/federicodecillia/easyprophet/badge.svg?branch=main)](https://coveralls.io/github/federicodecillia/easyprophet?branch=main)
[![GitHub issues](https://img.shields.io/github/issues/federicodecillia/easyprophet)](https://github.com/federicodecillia/easyprophet/issues)

Python package developed to simplify [**Prophet**](https://facebook.github.io/prophet/) application to any data. \
It completely relies on the [**Prophet package**](https://github.com/facebook/prophet) and on its updates.


# Installation
The package is normally released on pypy, you can find it [**here**](https://pypi.org/project/easyprophet/), and install it easily on your environment by typing:
`pip install easyprophet`

Note: Prophet requires pystan, that has its own [installation instructions](https://pystan2.readthedocs.io/en/latest/windows.html#windows)
on windows. It's recommended to use Conda Environment, and to perform the following step-by-step installation:
   1. Create and activate a conda environment: `conda create -n prophet_env`, `activate stan_env`
   2. install c++ compiler: `conda install libpython m2w64-toolchain -c msys2`
   3. install pystan dependencies through conda: `conda install numpy cython matplotlib scipy pandas pystan -c conda-forge`
   4. install prophet: `pip install prophet`

For more details about the installation of prophet, please check [the original documentation](https://facebook.github.io/prophet/docs/installation.html). 

# Project Structure

```
.
- notebooks              <- Jupyter/Colab Notebooks containing easyprophet examples
- src                    <- Source code for easy_prophet
    - easyprophet
        - __init__.py    <- To initialize easyprophet package
        - easyprophet.py <- Core easyprophet clasees & functions
        - hello_world.py <- module to test if the installation works
        - tools          <- Other helper scripts        
- tests                  <- Test suite
- .gitignore             <- Specifies intentionally untracked files to ignore
- AUTHORS.md             <- Credits
- CHANGELOG.md           <- Specify changes and features introduced in any release
- CODE_OF_CONDUCT.md     <- Code of conduct to which contributors must adhere
- LICENSE                <- License 
- README.md              <- This File! Contains info & links about the project
- requirements.txt       <- Python dependencies
- setup.py               <- Build script for setuptools (to make the pack pip installable)
- tox.ini                <- Contains info about the python tox test environment
```
