'''
# Description
This module handles the solving of the hamiltonian eigenvalues and eigenvectors for a given system.

# Index
- `get_laplacian_matrix()`
- `hamiltonian_matrix()`
- `potential()`
- `schrodinger()`
- `energies()`
- `interpolate_potential()`

---
'''


from .classes import *
from . import potentials
from . import file
from copy import deepcopy
import time
import numpy as np
from scipy import sparse
from scipy.interpolate import CubicSpline


# Second derivative matrix, according to the finite difference method
def get_laplacian_matrix(x):
    '''Returns the Laplacian matrix for a given grid x.'''
    diagonals = [-2*np.ones(len(x)), np.ones(len(x)), np.ones(len(x))]
    laplacian_matrix = sparse.spdiags(diagonals, [0, -1, 1], format='lil')
    # Periodic boundary conditions
    laplacian_matrix[0, -1] = 1
    laplacian_matrix[-1, 0] = 1
    dx = x[1] - x[0]
    laplacian_matrix /= dx**2
    return laplacian_matrix


def hamiltonian_matrix(system:System):
    '''Returns the Hamiltonian matrix for a given `qrotor.classes.System` object.'''
    V = system.potential_values.tolist()
    potential = sparse.diags(V, format='lil')
    B = system.B
    x = system.grid
    H = -B * get_laplacian_matrix(x) + potential  # Original Hamiltonian
    # H = -laplacian_matrix(x) + (1/B)*diags(potential)  # In units of B ¿? CHECK
    return H


def potential(system:System) -> System:
    '''Solves the potential_values of the system, according to the potential name, by calling `qrotor.potentials.solve`'''
    V = potentials.solve(system)
    if system.correct_potential_offset is True:
        offset = min(V)
        V = V - offset
        system.corrected_potential_offset = offset
    system.potential_values = V
    return system


def schrodinger(system:System) -> System:
    '''Solves the Schrödinger equation for a given `qrotor.classes.System` object.'''
    time_start = time.time()
    V = system.potential_values
    H = hamiltonian_matrix(system)
    print(f'Solving Hamiltonian matrix of size {system.gridsize}...')
    # Solve eigenvalues with ARPACK in shift-inverse mode, with a sparse matrix
    eigenvalues, eigenvectors = sparse.linalg.eigsh(H, system.E_levels, which='LM', sigma=0, maxiter=10000)
    if any(eigenvalues) is None:
        print('WARNING:  Not all eigenvalues were found.\n')
    else: print('Done.\n')
    system.eigenvalues = eigenvalues
    system.potential_max = max(V)
    system.potential_min = min(V)
    system.energy_barrier = max(V) - min(eigenvalues)
    system.first_transition = eigenvalues[1] - eigenvalues[0]
    system.runtime = time.time() - time_start
    if system.save_eigenvectors == True:
        system.eigenvectors = eigenvectors
    system.eigenvalues_B = eigenvalues / system.B
    system.potential_max_B = system.potential_max / system.B
    return system


def energies(var, filename=None) -> Experiment:
    '''Solves the Schrödinger equation for a given `qrotor.classes.System` or `qrotor.classes.Experiment` object.\n
    If a filename is provided, the results are saved to a file.'''
    if isinstance(var, System):
        data = Experiment()
        data.system = [deepcopy(var)]
    elif isinstance(var, Experiment):
        data = deepcopy(var)
    else:
        raise ValueError('Input must be a System or Experiment object.')
    for system in data.system:
        system = potential(system)
        system = schrodinger(system)
    if filename:
        file.save(data, filename)
    return data


def interpolate_potential(system:System) -> System:
    '''Interpolates the current potential_values to a new grid of size `qrotor.classes.System.gridsize`'''
    V = system.potential_values
    grid = system.grid
    gridsize = system.gridsize

    new_grid = np.linspace(0, 2*np.pi, gridsize)
    cubic_spline = CubicSpline(grid, V)
    new_V = cubic_spline(new_grid)

    system.grid = new_grid
    system.potential_values = new_V
    return system

