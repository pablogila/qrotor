import qrotor as qr
import numpy as np
from math import sqrt


variables = qr.Variables()
data = qr.Data()

gridsizes = [1000, 2000, 3000, 5000, 10000, 15000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000, 125000, 150000, 175000, 200000, 250000, 300000, 400000, 500000]

variables.potential_name = 'zero'
variables.B = 1
variables.searched_E_levels = 10
variables.check_E_level = 9  # Starting from 0

# Ideal_E can be set automatically for a zero potential
variables.get_ideal_E()
real_E_level = int(sqrt(variables.ideal_E))

variables.comment = f'Convergence test for the energy level #{variables.check_E_level}'
if variables.ideal_E:
    variables.comment += f' (n={real_E_level})'

for gridsize in gridsizes:

    variables.gridsize = gridsize
    variables.grid = np.linspace(0, 2*np.pi, gridsize)

    convergence_data = qr.solve.energies(variables, qr.out_file)
    data.add(convergence_data)

#qr.plot.convergence(data)

