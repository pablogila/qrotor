import qrotor as qr
import numpy as np
from math import sqrt


# Optimal gridsize value found in the convergence test
gridsize = 200000

file = qr.logdirfile

variables = qr.Variables()
variables.potential_name = 'titov2023'
variables.potential_constants = qr.constants_titov2023[0]
variables.B = qr.B_Hydrogen
variables.atom_type = 'H'
variables.searched_E_levels = 5
variables.gridsize = gridsize
variables.grid = np.linspace(0, 2*np.pi, gridsize)
variables.comment = f'Energies from titov2023. Reproduced with QRotor, gridsize {gridsize}'

data = qr.solve.energies(variables, file)

qr.file.compress(file)

