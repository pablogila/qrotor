import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh
import matplotlib.pyplot as plt
import time
import os


# The Hamiltonian is built via finite difference method, with periodic B.C.
#          [  2 -1  0  0  1 ]           [ V(0)                ]
#          [ -1  2 -1  0  0 ]           [    V(1)             ]
# H = -B * [  0 -1  2 -1  0 ] / dx**2 + [        V(2)         ]
#          [  0  0 -1  2 -1 ]           [            V(3)     ]
#          [  1  0  0 -1  2 ]           [                V(4) ]


class Variables:
    def __init__(self):
        self.comment = None
        self.runtime = None
        self.atom_type = None
        self.constants = None
        self.set_of_constants = None
        self.searched_E_levels = None
        self.potential_name = None
        self.potential = None
        self.B = None
        self.N = None
        self.x = None


class Solutions:
    def __init__(self):
        self.comment = None
        self.potential = None
        self.max_potential = None
        self.min_potential = None
        self.corrected_offset_potential = None
        self.eigenvalues = None
        self.eigenvectors = None
        self.energy_barrier = None
        self.first_transition = None


class Data:
    def __init__(self):
        self.title = None
        self.comment = None
        self.x = None
        self.set_of_potentials = None
        self.set_of_constants = None  # I want to get rid of this
        self.set_of_energies = None
        self.set_of_energies_H = None
        self.set_of_energies_D = None
        self.set_of_eigenvectors = None
        self.set_of_eigenvectors_H = None
        self.set_of_eigenvectors_D = None


# Redirect to the desired potential energy function
def V(variables:Variables):
    if variables.potential_name == 'titov2023':
        return potential_titov2023(variables)
    elif variables.potential_name == 'zero':
        return potential_zero(variables)
    else:
        return potential_custom(variables)


# Potential energy function of the hindered methyl rotor, from titov2023
def potential_titov2023(variables:Variables):
    x = variables.x
    C = variables.constants
    return C[0] + C[1] * np.sin(3*x) + C[2] * np.cos(3*x) + C[3] * np.sin(6*x) + C[4] * np.cos(6*x)


# Zero potential
def potential_zero(variables:Variables):
    x = variables.x
    return 0 * x


def potential_custom(variables:Variables):
    x = variables.x
    C = variables.constants
    phase = 0
    return C[0] + C[1] * np.cos(3*x + phase)  # A potential as an array resulting from DFT calculations, etc.


# Second derivative matrix, according to the finite difference method
def laplacian_matrix(x):
    diagonals = [-2*np.ones(len(x)), np.ones(len(x)-1), np.ones(len(x)-1)]
    laplacian_matrix = diags(diagonals, [0, -1, 1]).toarray()
    # Periodic boundary conditions
    laplacian_matrix[0, -1] = 1
    laplacian_matrix[-1, 0] = 1
    dx = x[1] - x[0]
    laplacian_matrix /= dx**2
    return laplacian_matrix


def hamiltonian_matrix(variables:Variables):
    potential = variables.potential
    B = variables.B
    x = variables.x
    H = -B * laplacian_matrix(x) + diags(potential)  # Original Hamiltonian
    # H = -laplacian_matrix(x) + (1/B)*diags(potential)  # In units of B
    return H


# Solve the Hamiltonian eigenvalues for the time independent Schrödinger equation.
def solve_energies(variables:Variables):
    potential = V(variables)
    offset = min(potential)
    potential = potential - offset
    variables.potential = potential
    
    H = hamiltonian_matrix(variables)

    eigenvalues, eigenvectors = eigsh(H, variables.searched_E_levels, which='SM')
    solutions = Solutions()
    solutions.potential = potential
    solutions.max_potential = max(potential)
    solutions.min_potential = min(potential)
    solutions.corrected_offset_potential = offset
    solutions.eigenvalues = eigenvalues
    solutions.eigenvectors = eigenvectors
    solutions.energy_barrier = max(potential) - min(eigenvalues)
    solutions.first_transition = eigenvalues[1] - eigenvalues[0]
    return solutions


# Recurrently solve the energies for a set of potential constants, and print the solutions.
def solve_variables(variables:Variables, out_file=None):
    set_of_energies = []
    set_of_eigenvectors = []
    set_of_potentials = []
    for C in variables.set_of_constants:
        variables.constants = C
        solutions = solve_energies(variables)
        solutions.comment = f'Potential constants:    {C}\n'
        print_solutions(solutions, out_file)

        set_of_energies.append(solutions.eigenvalues)
        set_of_eigenvectors.append(solutions.eigenvectors)
        set_of_potentials.append(solutions.potential)

    data = Data()
    data.set_of_energies = set_of_energies
    data.set_of_eigenvectors = set_of_eigenvectors
    data.set_of_potentials = set_of_potentials

    return data


def print_solutions(solutions:Solutions, out_file=None, print_eigenvectors=False):
    output = solutions.comment
    output += f'Max potential [meV]:    {solutions.max_potential:.4f}\n'
    output += f'Min potential [meV]:    {solutions.min_potential:.4f}\n'
    output += f'Corrected offset [meV]: {solutions.corrected_offset_potential:.4f}\n'
    output += f'Eigenvalues [meV]:      '
    for value in solutions.eigenvalues:
        output += f'{value:.4f} '
    output += '\n'
    output += f'Energy barrier [meV]:   {solutions.energy_barrier:.4f}\n'
    output += f'E1-E0 transition [meV]: {solutions.first_transition:.4f}\n'
    if print_eigenvectors:
        output += f'Eigenvectors [meV]:\n'
        for value in solutions.eigenvectors:
            output += f'{value}\n'
        output += '\n'
    output += '\n'

    print(output)
    if out_file:
        with open(out_file, 'a') as f:
            f.write(output)


def print_variables(variables:Variables, out_file=None):
    output = '\n' + variables.comment + '\n'
    output += f'Potential name:         {variables.potential_name}\n'
    output += f'Atom type:              {variables.atom_type}\n'
    output += f'Inertia B [meV]:        {variables.B:.4f}\n'
    output += f'Grid size N:            {variables.N}\n'
    output += f'Energy levels computed: {variables.searched_E_levels}\n'
    output += f'Runtime [s]:            {variables.runtime:.2f}\n'
    output += '\n\n'
    output += '------------------------------------\n\n'

    print(output)
    if out_file:
        with open(out_file, 'a') as f:
            f.write(output)


def plot_energies_and_potentials(data:Data):

    xlabel = 'Angle / radians'
    ylabel = 'Energy / meV'
    title = data.title
    V_color = 'C0'
    V_label = 'Potential'

    default_color = 'red'
    default_edgecolor = 'tomato'
    default_linestyle = '-'
    default_label = 'Energies'

    H_color = 'orange'
    H_edgecolor = 'peachpuff'
    H_linestyle = ':'
    H_label = 'H energies'

    D_color = 'orchid'
    D_edgecolor = 'lavender'
    D_linestyle = 'dashed'
    D_label = 'D energies'

    for i, potential in enumerate(data.set_of_potentials):
        # Plot potential energy
        plt.figure(figsize=(10, 6))
        plt.plot(data.x, potential, color=V_color, label=V_label)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(f'{title} (#' + str(i+1) + ')' )
        plt.xticks([0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi],
                   ['0', r'$\frac{\pi}{2}$', r'$\pi$', r'$\frac{3\pi}{2}$', r'$2\pi$'])
        # Plot default set_of_energies
        if data.set_of_energies:
            for j, energy in enumerate(data.set_of_energies[i]):
                plt.axhline(y=energy, color=default_color, linestyle=default_linestyle)
                plt.text(j%3*0.9, energy, f'E$_{j}$ = {energy:.4f}', va='top', bbox=dict(edgecolor=default_edgecolor, boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
            plt.plot([], [], color=default_color, label=default_label)  # Add to legend
        # Plot HYDROGEN set_of_energies_H
        if data.set_of_energies_H:
            for j, energy in enumerate(data.set_of_energies_H[i]):
                plt.axhline(y=energy, color=H_color, linestyle=H_linestyle)
                plt.text(j%3*0.9, energy, f'E$_{j}$ = {energy:.4f}', va='top', bbox=dict(edgecolor=H_edgecolor, boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
            plt.plot([], [], color=H_color, linestyle=H_linestyle, label=H_label)
        # Plot DEUTERIUM set_of_energies_D
        if data.set_of_energies_D:
            for j, energy in enumerate(data.set_of_energies_D[i]):
                plt.axhline(y=energy, color = D_color, linestyle=D_linestyle)
                plt.text(4+j%3*0.9, energy, f'E$_{j}$ = {energy:.4f}', va='top', bbox=dict(edgecolor=D_edgecolor, boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
            plt.plot([], [], color=D_color, linestyle=D_linestyle, label=D_label)  # Add to legend
        plt.subplots_adjust(right=0.85)
        plt.legend(bbox_to_anchor=(1.1, 0.5), loc='center', fontsize='small')
        plt.show()


##### TO-DO
def plot_eigenvectors(data:Data, levels=None, squared=False, scaling_factor=1):

    xlabel = 'Angle / radians'
    ylabel = 'Energy / meV'
    title = data.title
    V_color = 'lightblue'
    V_label = 'Potential'

    #energy_color = 'red'
    energy_edgecolor = 'lightgrey'
    energy_linestyle = ':'
    energy_label = 'E'

    eigenvector_linestyle = '--'

    # To square the eigenvectors
    if squared:
        eigenvector_label = 'Eigenvect$^2$ '
        square = 2
    else:
        eigenvector_label = 'Eigenvect '
        square = 1
    
    for i, potential in enumerate(data.set_of_potentials):

        # Transpose the 2D array so that each inner array represents a different eigenvector
        eigenvectors_transposed = np.transpose(data.set_of_eigenvectors[i])

        # Plot potential energy
        plt.figure(figsize=(10, 6))
        plt.plot(data.x, potential, color=V_color, label=V_label)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(f'{title} (#' + str(i+1) + ')' )
        if len(data.set_of_potentials) == 1:
            plt.title(f'{title}')
        plt.xticks([0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi],
                   ['0', r'$\frac{\pi}{2}$', r'$\pi$', r'$\frac{3\pi}{2}$', r'$2\pi$'])
        for j, energy in enumerate(data.set_of_energies[i]):
            if levels is not None and j not in levels:
                continue

            color = 'C' + str(j)

            E_label = energy_label + str(j)
            plt.axhline(y=energy, linestyle=energy_linestyle, color=color, label=E_label)
            plt.text(j%3*0.9, energy, f'E$_{j}$ = {energy:.4f}', va='top', bbox=dict(edgecolor=energy_edgecolor, boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))

            eigenvect_label = eigenvector_label + str(j)
            eigenvector = scaling_factor*eigenvectors_transposed[j]**square
            plt.plot(data.x, eigenvector, linestyle=eigenvector_linestyle, label=eigenvect_label, color=color)

        plt.subplots_adjust(right=0.85)
        plt.legend(bbox_to_anchor=(1.1, 0.5), loc='center', fontsize='small')
        plt.text(1.03, 0.9, f'Eigenvects\nscaled x{scaling_factor}', transform=plt.gca().transAxes)
        plt.show()


#################################
##########  CONSTANTS  ##########
#################################

# Output file
filename = 'eigenvalues.txt'
script_dir = os.path.dirname(os.path.abspath(__file__))
out_file = os.path.join(script_dir, filename)


# Atomic masses
m_H = 1.00784      # H mass
m_D = 2.014102     # D mass
# Methyl rotor radius
r = 0.537  # in meV  # 1.035 angstroms for MAI... CHECK UNITS
# Inertia. Should be 0.574 for H, according to titov2023
B_Hydrogen = 1.0 / (2 * 3*(m_H * r**2))
B_Deuterium = 1.0 / (2 * 3*(m_D * r**2))


# Potential constants from titov2023 [C1, C2, C3, C4, C5]
constants_zero = [
    [0,0,0,0,0]
    ]
constants_titov_1 = [
    [2.7860, 0.0130,-1.5284,-0.0037,-1.2791],
    [2.6507, 0.0158,-1.4111,-0.0007,-1.2547],
    [2.1852, 0.0164,-1.0017, 0.0003,-1.2061],
    [5.9109, 0.0258,-7.0152,-0.0168, 1.0213],
    [1.4526, 0.0134,-0.3196, 0.0005,-1.1461]
    ]
constants__titov_2 = [
    [2.7860, 0.0130,-1.5284,-0.0037,-1.2791],
    [3.0720, 0.0166,-1.8427,-0.0029,-1.2515],
    [2.7770, 0.0100, 1.7292,-0.0131,-0.9675],
    [5.4923,-0.0071,-6.4753,-0.0067, 0.9119],
    [3.2497, 0.0088, 2.3223,-0.0069,-0.8778],
    [4.4449, 0.0091, 4.8613,-0.0138, 0.5910]
    ]


# Instantiate objects. These are used to pass data between functions.
variables = Variables()


# Choose the set of constants to use
variables.set_of_constants = constants_titov_1 #constants_titov_1
variables.potential_name = 'titov2023'  # 'titov2023' or 'zero'
# Number of energy levels to calculate
variables.searched_E_levels = 5
# Grid size
variables.N = 100
variables.x = np.linspace(0, 2*np.pi, variables.N)


####################################
##########  MAIN PROGRAM  ##########
####################################


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

