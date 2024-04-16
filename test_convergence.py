import qrotor as qr
import numpy as np
import time
from math import sqrt


variables = qr.Variables()

variables.potential_name = 'zero'
#variables.atom_type = 'H'
variables.write_summary = True
variables.B = 1
variables.searched_E_levels = 5

# Convergence parameters
variables.check_E_level = 4  # Starting from 0
variables.check_E_difference = False
variables.plot_label = True  # Can be a bool, or a str for a label title
print_runtime = True
# Ideal_E is set automatically for a zero potential
variables.get_ideal_E()
real_E_level = int(sqrt(variables.ideal_E))

# SciPy seems to have convergence problems with matrices bigger than 5000-7500 ¿?
gridsizes = [100, 250, 500, 750, 1000, 1250, 1500, 1750, 2000, 2500, 3000, 4000, 5000, 6000, 7000, 10000]  

variables.comment = f'Convergence test for the energy level {variables.check_E_level}'
if variables.ideal_E:
    variables.comment += f' (n={real_E_level})'

data = qr.Data()
for gridsize in gridsizes:

    variables.gridsize = gridsize
    variables.grid = np.linspace(0, 2*np.pi, gridsize)

    convergence_data = qr.solve.energies(variables, qr.out_file)
    data.add(convergence_data)

# Remove runtimes from data
if not print_runtime:
    for solution in data.solutions:
        solution.runtime = None

qr.plot.convergence(data)

