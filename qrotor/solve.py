"""
# Description

This module is used to solve the hamiltonian eigenvalues and eigenvectors for a given quantum system.
Sparse matrices are used to achieve optimal performance.


# Index

| | |
| --- | --- |
| `laplacian_matrix()`      | Calculate the second derivative matrix for a given grid |
| `hamiltonian_matrix()`    | Calculate the hamiltonian matrix of the system |
| `potential()`             | Solve the potential values of the system |
| `schrodinger()`           | Solve the Schrödiger equation for the system |
| `energies()`              | Solve the system(s) for the QSys or QExp object |

---
"""


from .classes import *
from .potential import solve as solve_potential
from copy import deepcopy
import time
import numpy as np
from scipy import sparse
import aton


def laplacian_matrix(grid):
    """Calculates the Laplacian (second derivative) matrix for a given `grid`."""
    x = grid
    diagonals = [-2*np.ones(len(x)), np.ones(len(x)), np.ones(len(x))]
    laplacian_matrix = sparse.spdiags(diagonals, [0, -1, 1], format='lil')
    # Periodic boundary conditions
    laplacian_matrix[0, -1] = 1
    laplacian_matrix[-1, 0] = 1
    dx = x[1] - x[0]
    laplacian_matrix /= dx**2
    return laplacian_matrix


def hamiltonian_matrix(system:QSys):
    """Calculates the Hamiltonian matrix for a given `qrotor.classes.QSys` object."""
    V = system.potential_values.tolist()
    potential = sparse.diags(V, format='lil')
    B = system.B
    x = system.grid
    H = -B * laplacian_matrix(x) + potential
    return H


def potential(system:QSys) -> QSys:
    """Solves the potential_values of the system.

    It uses the potential name, by calling `qrotor.potential.solve`.
    Then it applies extra operations, such as removing the potential offset
    if `QSys.correct_potential_offset = True`.
    """
    V = solve_potential(system)
    if system.correct_potential_offset is True:
        offset = min(V)
        V = V - offset
        system.corrected_potential_offset = offset
    system.potential_values = V
    return system


def schrodinger(system:QSys) -> QSys:
    """Solves the Schrödinger equation for a given `qrotor.classes.QSys` object.
    
    Uses ARPACK in shift-inverse mode to solve the hamiltonian sparse matrix.
    """
    time_start = time.time()
    V = system.potential_values
    H = hamiltonian_matrix(system)
    print(f'Solving Hamiltonian matrix of size {system.gridsize}...')
    # Solve eigenvalues with ARPACK in shift-inverse mode, with a sparse matrix
    eigenvalues, eigenvectors = sparse.linalg.eigsh(H, system.E_levels, which='LM', sigma=0, maxiter=10000)
    if any(eigenvalues) is None:
        print('WARNING:  Not all eigenvalues were found.\n')
    else: print('Done.\n')
    system.runtime = time.time() - time_start
    system.eigenvalues = eigenvalues
    system.potential_max = max(V)
    system.potential_min = min(V)
    system.energy_barrier = max(V) - min(eigenvalues)
    system.first_transition = eigenvalues[1] - eigenvalues[0]
    if system.save_eigenvectors == True:
        system.eigenvectors = eigenvectors
    system.eigenvalues_B = eigenvalues / system.B
    system.potential_max_B = system.potential_max / system.B
    return system


def energies(var, filename:str=None) -> QExp:
    """Solves the Schrödinger equation for a given `qrotor.classes.QSys` or `qrotor.classes.QExp` object."""
    if isinstance(var, QSys):
        data = QExp()
        data.systems = [deepcopy(var)]
    elif isinstance(var, QExp):
        data = deepcopy(var)
    else:
        raise ValueError('Input must be a QSys or QExp object.')
    for system in data.systems:
        system = potential(system)
        system = schrodinger(system)
    if filename:
        aton.st.file.save(data, filename)
    return data

