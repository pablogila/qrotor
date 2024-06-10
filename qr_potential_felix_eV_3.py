import os
import qrotor as qr

in_filename = 'potential_felix.dat'
in_file = os.getcwd() + '/' + in_filename
#out_file = qr.logdirfile + '_potential_felix_eV_301'
#out_file = qr.logdirfile + '_potential_felix_meV_301'
out_file = qr.logdirfile + '_potential_felix_eV_3'
#out_file = qr.logdirfile + '_potential_felix_meV_3'

#I = 301.54  # amu Angstrom²
I = 3 * 1.00784 * 1.035**2
I = I * qr.amu_to_kg * qr.angstrom_to_m**2
B = ((qr.hbar**2) / (2 * I)) * qr.J_to_eV #* qr.eV_to_meV

variables = qr.Variables()
#variables.comment = f'{in_filename}, as eV, I = 301.54 amu AA**2'
#variables.comment = f'{in_filename}, as meV, I = 301.54 amu AA**2'
variables.comment = f'{in_filename}, as eV, I = 3.23887 amu AA**2'
#variables.comment = f'{in_filename}, as meV, I = 3.23887 amu AA**2'
variables.units = ['eV']
#variables.units = ['meV']
variables.B = B
variables.atom_type = 'H'
variables.searched_E_levels = 30
variables = qr.file.read_potential(variables, in_file)
variables.gridsize = 200000
variables = qr.solve.interpolate_potential(variables)

data = qr.solve.energies(variables)

qr.file.write(data, out_file)
qr.file.compress(out_file)

qr.plot.energies(data)

