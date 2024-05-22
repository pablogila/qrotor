import os
import qrotor as qr

in_filename = 'potential_felix.dat'
in_file = os.getcwd() + '/' + in_filename
out_file = qr.logdirfile + '_potential_felix'

variables = qr.Variables()
variables.searched_E_levels = 5
variables.units = ['eV']
I = 301.54  # amu Angstrom²
variables.B = 1.0 / (2 * I)
variables = qr.file.read_potential(variables, in_file)
variables.gridsize = 5000 #200000
variables = qr.solve.interpolate_potential(variables)
variables.comment = f'Calculated energies from {in_filename}'

data = qr.solve.energies(variables)

qr.file.write(data, out_file)
qr.file.compress(out_file)

# qr.plot.energies(data)

