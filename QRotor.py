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


class Solutions:
    def __init__(self):
        self.comment = None
        self.eigenvalues = None
        self.max_potential = None
        self.energy_barrier = None
        self.first_transition = None
        self.set_of_energies = None
        self.set_of_energies_H = None
        self.set_of_energies_D = None


class Variables:
    def __init__(self):
        self.comment = None
        self.runtime = None
        self.atom_type = None
        self.constants = None
        self.set_of_constants = None
        self.searched_energies = None
        self.potential = None
        self.m = None
        self.r = None
        self.B = None
        self.N = None
        self.x = None


# Potential energy function of the hindered methyl rotor, from titov2023
def V(x, C):
    return C[0] + C[1] * np.sin(3*x) + C[2] * np.cos(3*x) + C[3] * np.sin(6*x) + C[4] * np.cos(6*x)


# Second derivative matrix, according to the finite difference method
def second_derivative_matrix(x):
    diagonals = [-2*np.ones(len(x)), np.ones(len(x)-1), np.ones(len(x)-1)]
    second_derivative_matrix = diags(diagonals, [0, -1, 1]).toarray()
    # Periodic boundary conditions
    second_derivative_matrix[0, -1] = 1
    second_derivative_matrix[-1, 0] = 1
    dx = x[1] - x[0]
    second_derivative_matrix /= dx**2
    return second_derivative_matrix


# Solve the Hamiltonian eigenvalues for the time independent Schrödinger equation.
# Returns a Solutions object.
def solve_energies(variables:Variables):
    potential = V(variables.x, variables.constants)
    B = variables.B
    x = variables.x
    searched_energies = variables.searched_energies
    # Solve Hamiltoninan eigenvalues
    H = -B * second_derivative_matrix(x) + diags(potential)
    eigenvalues, _ = eigsh(H, searched_energies, which='SM')  # Omit the eigenvectors with '_'
    solutions = Solutions()
    solutions.eigenvalues = eigenvalues
    solutions.max_potential = max(potential)
    solutions.energy_barrier = max(potential) - min(eigenvalues)
    solutions.first_transition = eigenvalues[1] - eigenvalues[0]
    return solutions


# Solve for a set of potential constants, and print the solutions.
# Returns a list of eigenvalues for each set of constants.
def solve_variables(variables:Variables, out_file):
    set_of_energies = []
    for C in variables.set_of_constants:
        variables.constants = C
        solutions = solve_energies(variables)
        solutions.comment = f'Potential constants:    {C}'
        set_of_energies.append(solutions.eigenvalues)
        print_solutions(solutions, out_file)
    return set_of_energies


def print_solutions(solutions:Solutions, out_file=None):
    output = solutions.comment + '\n'
    output += f'Eigenvalues [meV]:      '
    for value in solutions.eigenvalues:
        output += f'{value:.4f} '
    output += '\n'
    output += f'Max potential [meV]:    {solutions.max_potential:.4f}\n'
    output += f'Energy barrier [meV]:   {solutions.energy_barrier:.4f}\n'
    output += f'E1-E0 transition [meV]: {solutions.first_transition:.4f}\n'
    output += '\n'

    print(output)
    if out_file:
        with open(out_file, 'a') as f:
            f.write(output)


def print_variables(variables:Variables, out_file=None):
    output = variables.comment + '\n'
    output += f'Atom type:              {variables.atom_type}\n'
    output += f'Inertia B [meV]:        {variables.B:.4f}\n'
    output += f'Grid size N:            {variables.N}\n'
    output += f'Energy levels computed: {variables.searched_energies}\n'
    output += f'Runtime [s]:            {variables.runtime:.2f}\n'
    output += '\n'
    output += '------------------------------------\n\n'

    print(output)
    if out_file:
        with open(out_file, 'a') as f:
            f.write(output)


def plot_solutions(solutions:Solutions, variables:Variables):

    xlabel = 'Angle / radians'
    ylabel = 'Energy / meV'
    title = 'Hindered methyl rotor potential'
    V_color = 'C0'
    V_label = 'Potential'

    H_color = 'C1'
    H_edgecolor = 'pink'
    H_linestyle = ':'
    H_label = 'H energies'

    D_color = 'C4'
    D_edgecolor = 'lightblue'
    D_linestyle = 'dashed'
    D_label = 'D energies'

    for i, C in enumerate(variables.set_of_constants):
        # Plot potential energy
        plt.figure(figsize=(10, 6))
        plt.plot(variables.x, V(variables.x, C), color=V_color, label=V_label)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(f'{title} (#' + str(variables.set_of_constants.index(C)+1) + ')' )
        plt.xticks([0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi],
                   ['0', r'$\frac{\pi}{2}$', r'$\pi$', r'$\frac{3\pi}{2}$', r'$2\pi$'])
        # Plot default set_of_energies
        if solutions.set_of_energies:
            for j, energy in enumerate(solutions.set_of_energies[i]):
                plt.axhline(y=energy, color='grey')
                plt.text(j%3*0.9, energy, f'E$_{j}$ = {energy:.4f}', va='top', bbox=dict(edgecolor='lightgrey', boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
            plt.plot([], [], color='grey', label='Energies')  # Add to legend
        # Plot HYDROGEN set_of_energies_H
        if solutions.set_of_energies_H:
            for j, energy in enumerate(solutions.set_of_energies_H[i]):
                plt.axhline(y=energy, color=H_color, linestyle=H_linestyle)
                plt.text(j%3*0.9, energy, f'E$_{j}$ = {energy:.4f}', va='top', bbox=dict(edgecolor=H_edgecolor, boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
            plt.plot([], [], color=H_color, linestyle=H_linestyle, label=H_label)
        # Plot DEUTERIUM set_of_energies_D
        if solutions.set_of_energies_D:
            for j, energy in enumerate(solutions.set_of_energies_D[i]):
                plt.axhline(y=energy, color = D_color, linestyle=D_linestyle)
                plt.text(4+j%3*0.9, energy, f'E$_{j}$ = {energy:.4f}', va='top', bbox=dict(edgecolor=D_edgecolor, boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
            plt.plot([], [], color=D_color, linestyle=D_linestyle, label=D_label)  # Add to legend
        plt.legend()
        plt.show()


####################################
##########  MAIN PROGRAM  ##########
####################################

# Output file
plot_results = True
filename = 'eigenvalues.txt'
script_dir = os.path.dirname(os.path.abspath(__file__))
out_file = os.path.join(script_dir, filename)


solutions = Solutions()
variables = Variables()

# Atomic masses
m_H = 1.00784      # H mass
m_D = 2.014102     # D mass

# Potential constants from titov2023 [C1, C2, C3, C4, C5]
constants_1 = [
    [2.7860, 0.0130,-1.5284,-0.0037,-1.2791],
    [2.6507, 0.0158,-1.4111,-0.0007,-1.2547],
    [2.1852, 0.0164,-1.0017, 0.0003,-1.2061],
    [5.9109, 0.0258,-7.0152,-0.0168, 1.0213],
    [1.4526, 0.0134,-0.3196, 0.0005,-1.1461]
    ]
constants_2 = [
    [2.7860, 0.0130,-1.5284,-0.0037,-1.2791],
    [3.0720, 0.0166,-1.8427,-0.0029,-1.2515],
    [2.7770, 0.0100, 1.7292,-0.0131,-0.9675],
    [5.4923,-0.0071,-6.4753,-0.0067, 0.9119],
    [3.2497, 0.0088, 2.3223,-0.0069,-0.8778],
    [4.4449, 0.0091, 4.8613,-0.0138, 0.5910]
    ]


# Choose the set of constants to use
variables.set_of_constants = constants_1
# Number of energy levels to calculate
variables.searched_energies = 5
# Grid size
variables.N = 1000
variables.x = np.linspace(0, 2*np.pi, variables.N)
# Methyl rotor radius
variables.r = 0.62  # 1.035  # ?? which value??


# Solve for HYDROGEN and print the results
variables.atom_type = 'H'
variables.m = m_H
variables.B = 1.0 / 2 * 3*(variables.m * variables.r**2)  # Inertia, 0.574 From titov2023

time_start = time.time()
solutions.set_of_energies_H = solve_variables(variables, out_file)
variables.runtime = time.time() - time_start
variables.comment = f'Summary of the last {len(solutions.set_of_energies_H)} calculations for a hindered methyl rotor:'
print_variables(variables, out_file)


# Change the atom type to DEUTERIUM and solve again
variables.atom_type = 'D'
variables.m = m_D
variables.B = 1.0 / 2 * 3*(variables.m * variables.r**2)

time_start = time.time()
solutions.set_of_energies_D = solve_variables(variables, out_file)
variables.runtime = time.time() - time_start
variables.comment = f'Summary of the last {len(solutions.set_of_energies_D)} calculations for a hindered methyl rotor:'
print_variables(variables, out_file)


print(f'Data saved to {filename}')


# Plots
if plot_results:
    plot_solutions(solutions, variables)

