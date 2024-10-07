from .core import *
from . import potentials
from . import file


# Second derivative matrix, according to the finite difference method
def laplacian_matrix_OLD(x):
    diagonals = [-2*np.ones(len(x)), np.ones(len(x)-1), np.ones(len(x)-1)]
    laplacian_matrix = sparse.diags(diagonals, [0, -1, 1]).toarray()
    # Periodic boundary conditions
    laplacian_matrix[0, -1] = 1
    laplacian_matrix[-1, 0] = 1
    dx = x[1] - x[0]
    laplacian_matrix /= dx**2
    return laplacian_matrix


def get_laplacian_matrix(x):
    diagonals = [-2*np.ones(len(x)), np.ones(len(x)), np.ones(len(x))]
    laplacian_matrix = sparse.spdiags(diagonals, [0, -1, 1], format='lil')
    # Periodic boundary conditions
    laplacian_matrix[0, -1] = 1
    laplacian_matrix[-1, 0] = 1
    dx = x[1] - x[0]
    laplacian_matrix /= dx**2
    return laplacian_matrix


def hamiltonian_matrix(variables:Variables):
    V = variables.potential_values.tolist()
    potential = sparse.diags(V, format='lil')
    B = variables.B
    x = variables.grid
    H = -B * get_laplacian_matrix(x) + potential  # Original Hamiltonian
    # H = -laplacian_matrix(x) + (1/B)*diags(potential)  # In units of B ¿? CHECK
    return H


def potential(variables:Variables):
    V = potentials.solve(variables)
    if variables.leave_potential_offset is not True:
        offset = min(V)
        V = V - offset
        variables.corrected_potential_offset = offset
    variables.potential_values = V
    return variables


def schrodinger(variables:Variables):
    time_start = time.time()

    V = variables.potential_values

    solutions = Solutions()

    H = hamiltonian_matrix(variables)
    print(f'Solving Hamiltonian matrix of size {variables.gridsize}...')
    # Solve eigenvalues with ARPACK in shift-inverse mode
    eigenvalues, eigenvectors = eigsh(H, variables.searched_E_levels, which='LM', sigma=0, maxiter=10000)
    if any(eigenvalues) is None:
        print('WARNING:  Not all eigenvalues were found.\n')
    else: print('Done.\n')

    solutions.eigenvalues = eigenvalues
    solutions.max_potential = max(V)
    solutions.min_potential = min(V)
    solutions.energy_barrier = max(V) - min(eigenvalues)
    solutions.first_transition = eigenvalues[1] - eigenvalues[0]
    solutions.runtime = time.time() - time_start
    if variables.save_eigenvectors == True:
        solutions.eigenvectors = eigenvectors

    solutions.eigenvalues_B = eigenvalues / variables.B
    solutions.max_potential_B = solutions.max_potential / variables.B
    #solutions.max_potential_B = variables.potential_constants[0] / variables.B
    return solutions


def energies(variables:Variables, out_file=None):
    data = Data()

    variables = potential(variables)

    solutions = schrodinger(variables)

    stored_variables = deepcopy(variables)

    data.variables.append(stored_variables)
    data.solutions.append(solutions)

    if out_file:
        stored_data = Data()
        stored_data.variables.append(stored_variables)
        stored_data.solutions.append(solutions)
        file.write(stored_data, out_file)

    return data


def interpolate_potential(variables:Variables):
    '''Interpolates the current potential_values to a new grid of size Variables.gridsize'''
    V = variables.potential_values
    grid = variables.grid
    gridsize = variables.gridsize

    new_grid = np.linspace(0, 2*np.pi, gridsize)
    cubic_spline = CubicSpline(grid, V)
    new_V = cubic_spline(new_grid)

    variables.grid = new_grid
    variables.potential_values = new_V
    return variables

