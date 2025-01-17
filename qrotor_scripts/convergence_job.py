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

variables.gridsize = gridsize
variables.grid = np.linspace(0, 2*np.pi, gridsize)

variables.comment = f'Convergence test for a grid of size {gridsize}'

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

