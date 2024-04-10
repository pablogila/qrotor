from qrotor.core import *


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
    # H = -laplacian_matrix(x) + (1/B)*diags(potential)  # In units of B ¿? CHECK
    return H


# Solve the Hamiltonian eigenvalues for the time independent Schrödinger equation.
def solve_hamiltonian(variables:Variables):
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
        solutions = solve_hamiltonian(variables)
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

