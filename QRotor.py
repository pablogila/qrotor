from qrotor.core import *

'''
########################################################################
# WE CAN JUST SOLVE IT ONCE, AND MULTIPLY BY B. WE NEED TO TEST IT.
# GENERIC WITH B=1 ??
variables.atom_type = 'Generic case'
variables.B = 1.0
time_start = time.time()
data_generic = solve_variables(variables, out_file)
variables.runtime = time.time() - time_start
variables.comment = f'Summary of the last {len(data_generic.set_of_energies)} calculations for a hindered methyl rotor:'
print_variables(variables, out_file)
#
print(f'Now lets multiply by B_Hydrogen: {B_Hydrogen}')
for energy in data_generic.set_of_energies:
    print(f'generic: {energy}')
    test = energy * B_Hydrogen
    print(f'test energies:    {test}')
#########  THIS IS A FAIL....
########################################################################
'''


# Solve for HYDROGEN and print the results
variables.atom_type = 'H'
variables.B = B_Hydrogen
time_start = time.time()
data_H = solve_variables(variables, out_file)
variables.runtime = time.time() - time_start
variables.comment = f'Summary of the last {len(data_H.set_of_energies)} calculations for a hindered methyl rotor:'
print_variables(variables, out_file)


# Change the atom type to DEUTERIUM and solve again
variables.atom_type = 'D'
variables.B = B_Deuterium
time_start = time.time()
data_D = solve_variables(variables, out_file)
variables.runtime = time.time() - time_start
variables.comment = f'Summary of the last {len(data_D.set_of_energies)} calculations for a hindered methyl rotor:'
print_variables(variables, out_file)


print(f'Data saved to {filename}\n')


# Group H and D data in the same object, to plot them together
data = Data()
data.title = 'Hindered methyl rotor potential'
data.set_of_potentials = data_H.set_of_potentials  # Both are the same
data.set_of_energies_H = data_H.set_of_energies
data.set_of_eigenvectors_H = data_H.set_of_eigenvectors
data.set_of_energies_D = data_D.set_of_energies
data.set_of_eigenvectors_D = data_D.set_of_eigenvectors
data.set_of_constants = variables.set_of_constants
data.x = variables.x
plot_energies_and_potentials(data)


# Plot the eigenvalues for Hydrogen
data.title = 'Hindered methyl rotor eigenvalues'
data.set_of_energies = data.set_of_energies_H
data.set_of_eigenvectors = data.set_of_eigenvectors_H
plot_eigenvectors(data, [0,1,2,3,4], True, 100)

