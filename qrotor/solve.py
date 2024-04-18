from .common import *
from . import potentials
from . import file


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
    x = variables.grid
    H = -B * laplacian_matrix(x) + diags(V)  # Original Hamiltonian
    # H = -laplacian_matrix(x) + (1/B)*diags(potential)  # In units of B ¿? CHECK
    return H


def schrodinger(variables:Variables):
    time_start = time.time()

    V = variables.potential_values

    solutions = Solutions()

    solutions.max_potential = max(V)
    solutions.min_potential = min(V)

    H = hamiltonian_matrix(variables)
    # Solve eigenvalues with ARPACK in shift-inverse mode
    print(f'Solving Hamiltonian matrix of size {variables.gridsize}...')
    eigenvalues, eigenvectors = eigsh(H, variables.searched_E_levels, which='LM', sigma=0, maxiter=10000)
    if any(eigenvalues) is None:
        print('WARNING:  Not all eigenvalues were found.\n')
    else: print('Done.\n')

    solutions.eigenvalues = eigenvalues
    solutions.eigenvectors = eigenvectors
    solutions.energy_barrier = max(V) - min(eigenvalues)
    solutions.first_transition = eigenvalues[1] - eigenvalues[0]

    solutions.runtime = time.time() - time_start
    return solutions


def energies(variables:Variables, out_file=None):
    data = Data()

    if variables.set_of_constants is None:
        variables.set_of_constants = [[0]]
        if variables.potential_constants is not None:
            variables.set_of_constants = [variables.potential_constants]

    for constants in variables.set_of_constants:
        variables.potential_constants = constants
        variables = potential(variables)

        solutions = schrodinger(variables)
        # solutions.comment = f'{i+1}'

        stored_variables = deepcopy(variables)

        data.variables.append(stored_variables)
        data.solutions.append(solutions)

        if out_file:
            stored_data = Data()
            stored_data.variables.append(stored_variables)
            stored_data.solutions.append(solutions)
            file.write(stored_data, out_file)

    return data


def potential(variables:Variables):
    V = potentials.solve(variables)
    if variables.leave_potential_offset is not True:
        offset = min(V)
        V = V - offset
        variables.corrected_potential_offset = offset
    variables.potential_values = V
    return variables


def grid_2pi(variables:Variables):
    variables.grid = np.linspace(0, 2*np.pi, variables.gridsize)
    return variables

