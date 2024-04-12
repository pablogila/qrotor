import qrotor as qr
import numpy as np
import time

variables = qr.Variables()

variables.potential = 'zero'
variables.searched_E_levels = 10
variables.atom_type = 'H'
variables.B = 1

convergence_test = qr.Convergence()
convergence_test.energies = []
convergence_test.runtimes = []
convergence_test.gridsizes = [100, 250, 500, 750, 1000, 1250, 1500, 1750, 2000, 2500, 3000, 4000, 5000]  # sccipy has convergence problems with matrices bigger than 5000-7500

convergence_test.energy_level = 9

if convergence_test.energy_level % 2 == 0:
    real_energy_level = convergence_test.energy_level / 2
else: real_energy_level = (convergence_test.energy_level + 1) / 2
convergence_test.ideal = real_energy_level ** 2

convergence_test.title = f'Convergence test for the energy level {convergence_test.energy_level} (n={int(real_energy_level)})'


for gridsize in convergence_test.gridsizes:

    variables.N = gridsize
    variables.x = np.linspace(0, 2*np.pi, variables.N)

    time_start = time.time()
    data = qr.solve.energies(variables, qr.out_file)
    variables.runtime = time.time() - time_start

    variables.comment = f'Parameters of the last convergence calculation for a grid of size N={gridsize}:'
    qr.write.variables(variables, qr.out_file)

    convergence_test.runtimes.append(variables.runtime)
    convergence_test.energies.append(data.set_of_energies)

qr.plot.energy_convergence(convergence_test)

