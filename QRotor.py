import qrotor as qr
import os


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


variables = qr.variables

# Solve for HYDROGEN and print the results
variables.atom_type = 'H'
variables.B = qr.B_Hydrogen
time_start = time.time()
data_H = qr.solve.energies(variables, qr.out_file)
variables.runtime = time.time() - time_start
variables.comment = f'Summary of the last {len(data_H.set_of_energies)} calculations for a hindered methyl rotor:'
qr.write.variables(variables, qr.out_file)


# Change the atom type to DEUTERIUM and solve again
variables.atom_type = 'D'
variables.B = qr.B_Deuterium
time_start = time.time()
data_D = qr.solve.energies(variables, qr.out_file)
variables.runtime = time.time() - time_start
variables.comment = f'Summary of the last {len(data_D.set_of_energies)} calculations for a hindered methyl rotor:'
qr.write.variables(variables, qr.out_file)




# Group H and D data in the same object, to plot them together
data = qr.Data()
data.title = 'Hindered methyl rotor potential'
data.set_of_potentials = data_H.set_of_potentials  # Both are the same
data.set_of_energies_H = data_H.set_of_energies
data.set_of_eigenvectors_H = data_H.set_of_eigenvectors
data.set_of_energies_D = data_D.set_of_energies
data.set_of_eigenvectors_D = data_D.set_of_eigenvectors
data.set_of_constants = variables.set_of_constants
data.x = variables.x
qr.plot.energies(data)


# Plot the eigenvalues for Hydrogen
data.title = 'Hindered methyl rotor eigenvalues'
data.set_of_energies = data.set_of_energies_H
data.set_of_eigenvectors = data.set_of_eigenvectors_H
qr.plot.eigenvectors(data, [0,1,2,3,4], True, 100)


'''


variables = qr.variables

# Solve for HYDROGEN and print the results
variables.atom_type = 'H'
variables.B = qr.B_Hydrogen
variables.comment = 'Hindered methyl rotor potential'

filename = 'test.json'
out_file = os.path.join(os.getcwd(), filename)

data = qr.solve.energies(variables, out_file)

qr.plot.energies(data)

'''
datatest = qr.read.data('test.json')

print(datatest.solutions[0].eigenvalues)
print(datatest.variables[0].N)
print(datatest.variables[3].N)

qr.plot.energies(datatest)


'''

