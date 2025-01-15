"""
# ⚠️ UNDER DEVELOPMENT

THIS PACKAGE IS STILL UNDER HEAVY DEVELOPMENT, DON'T USE IT


# Description
 
The QRotor subpackage is used to study the quantum energy levels of rotating methyl and amine groups.


# Index

| | |
| --- | --- |
| `qrotor.classes`   | Definition of the `QSys` and `QExp` classes |
| `qrotor.constants` | Bond lengths and inertias |
| `qrotor.rotate`    | Rotate specific atoms from structural files |
| `qrotor.solve`     | Solve rotation eigenvalues and eigenvectors |
| `qrotor.potential` | Potential definitions and loading functions |
| `qrotor.plot`      | Plotting functions |

"""

from .classes import QSys, QExp
from .constants import *
from . import potential
from . import solve
from . import rotate
from . import plot        ###### TODO: update

