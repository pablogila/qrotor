import qrotor as qr
import numpy as np
from math import sqrt
import os


##########  Replaced by convergence_sbatch.py  ##########
this_script_is_a_copy=False
gridsize=1000
slurm_file='/path/to/slurm'
########################################################


file = qr.logdirfile + '_' + str(gridsize)

variables = qr.Variables()
variables.potential_name = 'zero'
variables.B = 1
variables.searched_E_levels = 10
variables.check_E_level = 9  # Starting from 0

variables.gridsize = gridsize
variables.grid = np.linspace(0, 2*np.pi, gridsize)

# Ideal_E can be set automatically for a zero potential
variables.get_ideal_E()
real_E_level = int(sqrt(variables.ideal_E))

variables.comment = f'Convergence test for the energy level #{variables.check_E_level}'
if variables.ideal_E:
    variables.comment += f' (n={real_E_level})'

data = qr.solve.energies(variables, file)

qr.file.compress(file)

# qr.plot.convergence(data)


# Clean copies of this script
if this_script_is_a_copy:
    this_script = os.path.basename(__file__)
    print(f'Calculation finished, removing this script:  {this_script}...')
    os.remove(slurm_file)
    os.remove(this_script)

#qr.plot.energies(data)

