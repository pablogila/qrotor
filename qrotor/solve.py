"""
# Description

This module is used to solve any given quantum system.

Although the functions of this module can be used independently,
it is highly recommended to use the methods `System.solve()` or
`System.solve_potential()` instead to solve the whole quantum system
or just the potential values.
These user methods perform all calculations automatically,
see `qrotor.system.System.solve()` and
`qrotor.system.System.solve_potential()` respectively for more details.

This documentation page is left for reference and advanced users only.


# Index

| | |
| --- | --- |
| `energies()`              | Solve the quantum system, including eigenvalues and eigenvectors |
| `potential()`             | Solve the potential values of the system |
| `schrodinger()`           | Solve the Schrödiger equation for the system |
| `hamiltonian_matrix()`    | Calculate the hamiltonian matrix of the system |
| `laplacian_matrix()`      | Calculate the second derivative matrix for a given grid |
| `excitations()`           | Get excitation levels and tunnel splitting energies |
| `E_levels`                | Group a list of degenerated eigenvalues by energy levels |

---
"""


from .system import System
from .potential import solve as solve_potential
from .potential import interpolate
import time
import numpy as np
from scipy import sparse
import aton
from ._version import __version__


def energies(system:System, filename:str=None) -> System:
    """Solves the quantum `system`.

    This includes solving the potential, the eigenvalues and the eigenvectors.

    The resulting System object is saved with pickle to `filename` if specified.
    """
    system = potential(system)
    system = schrodinger(system)
    if filename:
        aton.file.save(system, filename)
    return system


def potential(system:System, gridsize:int=None) -> System:
    """Solves the potential values of the `system`.

    Creates a grid if not yet present.
    It also interpolates the potential if `system.gridsize` is larger than the current grid;
    optionally, an alternative `gridsize` can be specified.

    It then solves the potential according to the potential name.
    Then it applies extra operations, such as removing the potential offset
    if `system.correct_potential_offset = True`.
    """
    if gridsize:
        system.gridsize = gridsize
    if not any(system.grid):
        system.set_grid()
    if system.gridsize and any(system.grid):
        if system.gridsize > len(system.grid):
            system = interpolate(system)
    V = solve_potential(system)
    if system.correct_potential_offset is True:
        offset = min(V)
        V = V - offset
        system.potential_offset = offset
    system.potential_max = max(V)
    system.potential_min = min(V)
    system.potential_values = V
    return system


def schrodinger(system:System) -> System:
    """Solves the Schrödinger equation for a given `system`.
    
    Uses ARPACK in shift-inverse mode to solve the hamiltonian sparse matrix.
    """
    time_start = time.time()
    V = system.potential_values
    H = hamiltonian_matrix(system)
    print('Solving Schrodinger equation...')
    # Solve eigenvalues with ARPACK in shift-inverse mode, with a sparse matrix
    eigenvalues, eigenvectors = sparse.linalg.eigsh(H, system.searched_E, which='LM', sigma=0, maxiter=10000)
    if any(eigenvalues) is None:
        print('WARNING:  Not all eigenvalues were found.\n')
    else: print('Done.')
    system.version = __version__
    system.runtime = time.time() - time_start
    system.eigenvalues = eigenvalues
    system.energy_barrier = max(V) - min(eigenvalues)
    # Solve excitations and tunnel splittings, assuming triplet degeneracy
    system = excitations(system)
    # Do we really need to save eigenvectors?
    if system.save_eigenvectors == True:
        system.eigenvectors = np.transpose(eigenvectors)
    # Save potential max and min, in case these are not already saved
    system.potential_max = max(V)
    system.potential_min = min(V)
    return system


def hamiltonian_matrix(system:System):
    """Calculates the Hamiltonian sparse matrix for a given `system`."""
    print(f'Creating Hamiltonian sparse matrix of size {system.gridsize}...')
    V = system.potential_values.tolist()
    potential = sparse.diags(V, format='lil')
    B = system.B
    x = system.grid
    H = -B * laplacian_matrix(x) + potential
    return H


def laplacian_matrix(grid):
    """Calculates the Laplacian (second derivative) matrix for a given `grid`."""
    x = grid
    n = len(x)
    diagonals = [-2*np.ones(n), np.ones(n), np.ones(n)]
    laplacian_matrix = sparse.spdiags(diagonals, [0, -1, 1], m=n, n=n, format='lil')
    # Periodic boundary conditions
    laplacian_matrix[0, -1] = 1
    laplacian_matrix[-1, 0] = 1
    dx = x[1] - x[0]
    laplacian_matrix /= dx**2
    return laplacian_matrix


def excitations(system: System) -> System:
    """Calculate the excitation levels and the tunnel splitting energies of a system.

    Automatically detects degenerated energy levels by looking at significant jumps
    between consecutive eigenvalues. Within each level, finds two subgroups
    to calculate tunnel splittings. Stops when energies reach the maximum potential.

    Excitations are calculated as the energy difference between the mean energy of the
    ground state level and the mean energy of each excited level.

    Tunnel splittings are calculated as the difference between the mean values of
    the two subgroups within each degenerate level.
    """
    # Get eigenvalues, stop before any possible None value
    eigenvalues = system.eigenvalues
    if not isinstance(eigenvalues, (list, np.ndarray)) or len(eigenvalues) == 0:
        return system
    if None in eigenvalues:
        none_index = eigenvalues.tolist().index(None)
        eigenvalues = eigenvalues[:none_index]
    if len(eigenvalues) < 3:
        return system
    # Group degenerated eigenvalues into energy levels
    levels, degeneracy = E_levels(eigenvalues, system.potential_max)
    system.E_levels = levels
    system.deg = degeneracy
    # Calculate excitations and splittings
    ground_energy = np.mean(levels[0])  # Mean of ground state level
    excitations = []
    tunnel_splittings = []
    for level in levels:
        level_mean = np.mean(level)
        excitations.append(level_mean - ground_energy)
        # Get the tunnel splitting within the level
        if len(level) > 1:
            # Find the largest gap within the level to split into two subgroups
            internal_gaps = np.diff(level)
            split_idx = np.argmax(internal_gaps) + 1
            # Split into two subgroups
            subgroup1 = level[:split_idx]
            subgroup2 = level[split_idx:]
            # Medians of subgroups
            median1 = np.median(subgroup1)
            median2 = np.median(subgroup2)
            # Tunnel splitting is the difference between medians
            tunnel_splittings.append(abs(median2 - median1))
        else:
            tunnel_splittings.append(0)
    system.excitations = excitations[1:]  # Exclude ground state
    system.splittings = tunnel_splittings
    return system


def E_levels(eigenvalues, vmax:float=None) -> list:
    """Group a list of degenerated eigenvalues by energy levels.

    Automatically detects degenerated energy levels by
    looking at significant jumps between consecutive eigenvalues.

    An optional `vmax` can be specified,
    to avoid including too many eigenvalues
    above a certain potential maximum.
    Only two more eigenvalues are considered after `vmax`,
    to properly detect energy levels around the maximum.

    Example:
    ```python
    levels, deg = qr.solve.E_levels(array([1.1, 1.2, 1.3, 5.4, 5.5, 5.6]))
    levels  # [array([1.1, 1.2, 1.3]), array([5.4, 5.5, 5.6])]
    deg  # 3
    ```
    """
    if vmax:  # Include all eigenvalues below Vmax plus 3 more eigenvalues
        # Check if any values are above vmax
        eigenvalues_above_vmax = eigenvalues > vmax
        if np.any(eigenvalues_above_vmax):
            index_first_above_vmax = np.where(eigenvalues_above_vmax)[0][0]
            eigenvalues = eigenvalues[:(index_first_above_vmax + 2)]
    # Group degenerated eigenvalues into energy levels
    for scale in np.arange(2, 4, 0.25):  # First search going to bigger scales
        levels, degeneracy = _get_E_levels_by_gap(eigenvalues, scale)
        if (degeneracy > 1) and (degeneracy % 1 == 0):
            break
        else:
            levels, degeneracy = None, None
    if not degeneracy:  # If it didn't work, search with tighter values
        for scale in np.arange(0.75, 2, 0.25):
            levels, degeneracy = _get_E_levels_by_gap(eigenvalues, scale)
            if (degeneracy > 1) and (degeneracy % 1 == 0):
                break
    if not (degeneracy > 1) and not (degeneracy % 1) == 0:
        return levels, degeneracy  # I give up
    # Correct the last two levels
    if len(levels) >= 2 and len(levels[-2]) != degeneracy:
        levels[-2] = np.concatenate((levels[-2], levels[-1]))
        levels.pop(-1)
    # Split last level into groups of size = degeneracy
    last_level = levels[-1]
    additional_levels = len(last_level) // degeneracy
    if additional_levels > 0:
        # Replace last level with list of complete degeneracy groups
        complete_groups = [last_level[i:i+degeneracy] for i in range(0, additional_levels*degeneracy, degeneracy)]
        levels.pop(-1)  # Remove original last level
        levels.extend(complete_groups)  # Add all complete groups
    else:
        levels.pop(-1)  # Remove incomplete last level
    return levels, degeneracy


def _get_E_levels_by_gap(eigenvalues, scale:float=2) -> tuple:
    """Split a list of eigenvalues into energy levels by looking at gaps.
    
    If the gap is bigger than the average gap times `scale`, it is considered a new level.

    Returns a tuple with the estimated levels and the average degeneracy.
    The last two levels are not taken into account to estimate the degeneracy.
    """
    # Find gaps between consecutive eigenvalues
    gaps = np.diff(eigenvalues)
    # Use mean gap times scale as threshold to distinguish energy levels
    med_gap = np.mean(gaps)
    level_breaks = np.where(gaps > scale * med_gap)[0] + 1
    levels = np.split(eigenvalues, level_breaks)
    # Calculate average degeneracy excluding last two levels if possible
    if len(levels) > 2:
        avg_degeneracy = float(np.mean([len(level) for level in levels[:-2]]))
    else:
        avg_degeneracy = float(len(levels[0]))
    if avg_degeneracy % 1 == 0:
        avg_degeneracy = int(avg_degeneracy)
    return levels, avg_degeneracy

