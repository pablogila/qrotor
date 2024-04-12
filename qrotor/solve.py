from .common import *
from . import potential
from . import write


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
    V = variables.potential_values
    B = variables.B
    x = variables.x
    H = -B * laplacian_matrix(x) + diags(V)  # Original Hamiltonian
    # H = -laplacian_matrix(x) + (1/B)*diags(potential)  # In units of B ¿? CHECK
    return H


# Solve the Hamiltonian eigenvalues for the time independent Schrödinger equation.
def schrodinger_OLD(variables:Variables):
    V = potential.V(variables)
    offset = min(V)
    V = V - offset
    variables.potential_values = V
    
    H = hamiltonian_matrix(variables)

    eigenvalues, eigenvectors = eigsh(H, variables.searched_E_levels, which='SM')
    solutions = Solutions()
    solutions.potential_values = V
    solutions.max_potential = max(V)
    solutions.min_potential = min(V)
    solutions.corrected_offset_potential = offset
    solutions.eigenvalues = eigenvalues
    solutions.eigenvectors = eigenvectors
    solutions.energy_barrier = max(V) - min(eigenvalues)
    solutions.first_transition = eigenvalues[1] - eigenvalues[0]
    return solutions


# Recurrently solve the energies for a set of potential constants, and print the solutions.
def energies_OLD(variables:Variables, out_file=None):
    set_of_energies = []
    set_of_eigenvectors = []
    set_of_potentials = []

    if variables.set_of_constants is None:
        variables.set_of_constants = [[0]]

    # Iterate over the potential constants inside the Variables object, and solve the Hamiltonian for each one.
    for i, C in enumerate(variables.set_of_constants):
        variables.potential_constants = C
        solutions = schrodinger(variables)
        solutions.constants = variables.potential_constants
        solutions.comment = f'{i+1}'
        write.solutions(solutions, out_file)

        set_of_energies.append(solutions.eigenvalues)
        set_of_eigenvectors.append(solutions.eigenvectors)
        set_of_potentials.append(solutions.potential_values)

    data = Data()
    data.set_of_energies = set_of_energies
    data.set_of_eigenvectors = set_of_eigenvectors
    data.set_of_potentials = set_of_potentials

    return data


def schrodinger(variables:Variables):
    time_start = time.time()

    V = variables.potential_values

    solutions = Solutions()

    solutions.max_potential = max(V)
    solutions.min_potential = min(V)

    H = hamiltonian_matrix(variables)
    eigenvalues, eigenvectors = eigsh(H, variables.searched_E_levels, which='SM')

    solutions.eigenvalues = eigenvalues
    solutions.eigenvectors = eigenvectors
    solutions.energy_barrier = max(V) - min(eigenvalues)
    solutions.first_transition = eigenvalues[1] - eigenvalues[0]

    solutions.runtime = time.time() - time_start
    return solutions, variables


def energies(variables:Variables, out_file=None):
    data = Data()

    if variables.set_of_constants is None:
        variables.set_of_constants = [[0]]
        if variables.potential_constants is not None:
            variables.set_of_constants = [variables.potential_constants]

    for i, constants in enumerate(variables.set_of_constants):
        variables.potential_constants = constants

        V = potential.V(variables)
        if variables.leave_potential_offset is not True:
            offset = min(V)
            V = V - offset
            variables.corrected_potential_offset = offset
        variables.potential_values = V

        solutions, new_variables = schrodinger(variables)

        solutions.comment = f'{i+1}'

        data_temp = Data()
        data_temp.variables.append(new_variables)
        data_temp.solutions.append(solutions)
        write.data(data_temp, out_file)

        data.variables.append(new_variables)
        data.solutions.append(solutions)

        # DEBUG
        print(new_variables.potential_constants)
        # For some weird reason, the potential constants are not being saved in the data object as they should.

    return data

