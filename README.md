# Prophet Pack

Python package developed to simplify [**Prophet**](https://facebook.github.io/prophet/) application to any data. \
It completely relies on the [**Prophet package**](https://github.com/facebook/prophet) and on its updates.

Project Structure
-----------------

```
.
- config                 <- Configuration files
- docs                   <- Documentation
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
- LICENSE                <- License 
- README.md              <- Contains info & links about the project
- requirements.txt       <- Package dependencies
- setup.py               <- Build script for setuptools (to make the pack pip installable)
```
