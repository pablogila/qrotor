"""
# Description

This module contains utility functions to handle multiple `qrotor.system` calculations.
These are commonly used as a list of `System` objects.


# Index

| | |
| --- | --- |
| `as_list()`          | Ensures that a list only contains System objects |
| `save_energies()`    | Save the energy eigenvalues for all systems to a CSV |
| `save_splittings()`  | Save the tunnel splitting energies for all systems to a CSV |
| `get_energies()`     | Get the eigenvalues from all systems |
| `get_gridsizes()`    | Get all gridsizes |
| `get_runtimes()`     | Get all runtimes |
| `get_groups()`       | Get the chemical groups in use |
| `get_ideal_E()`      | Calculate the ideal energy for a specified level |
| `sort_by_gridsize()` | Sort systems by gridsize |
| `reduce_size()`      | Discard data that takes too much space |
| `summary()`          | Print a summary of a System or list of Systems |

---
"""


from .system import System
from aton import txt
import pandas as pd


def as_list(systems) -> None:
    """Ensures that `systems` is a list of System objects.

    If it is a System, returns a list with that System as the only element.
    If it is neither a list nor a System,
    or if the list does not contain only System objects,
    it raises an error.
    """
    if isinstance(systems, System):
        systems = [systems]
    if not isinstance(systems, list):
        raise TypeError(f"Must be a System object or a list of systems, found instead: {type(systems)}")
    for i in systems:
        if not isinstance(i, System):
            raise TypeError(f"All items in the list must be System objects, found instead: {type(i)}")
    return systems


def save_energies(
        systems:list,
        comment:str='',
        filepath:str='eigenvalues.csv',
        ) -> pd.DataFrame:
    """Save the energy eigenvalues for all `systems` to a eigenvalues.csv file.

    Returns a Pandas Dataset with `System.comment` columns and `System.eigenvalues` values.

    The output file can be changed with `filepath`,
    or set to null to avoid saving the dataset.
    A `comment` can be included at the top of the file.
    Note that `System.comment` must not include commas (`,`).
    """
    as_list(systems)
    version = systems[0].version
    E = {}
    # Find max length of eigenvalues
    max_len = max((len(s.eigenvalues) if s.eigenvalues is not None else 0) for s in systems)
    for s in systems:
        if s.eigenvalues is not None:
            # Filter out None values and replace with NaN
            valid_eigenvalues = [float('nan') if e is None else e for e in s.eigenvalues]
            padded_eigenvalues = valid_eigenvalues + [float('nan')] * (max_len - len(s.eigenvalues))
        else:
            padded_eigenvalues = [float('nan')] * max_len
        E[s.comment] = padded_eigenvalues
    df = pd.DataFrame(E)
    if not filepath:
        return df
    # Else save to file
    df.to_csv(filepath, sep=',', index=False)
    # Include a comment at the top of the file
    file_comment = f'# {comment}\n' if comment else f''
    file_comment += f'# Energy eigenvalues\n'
    file_comment += f'# Calculated with QRotor {version}\n'
    file_comment += f'# https://pablogila.github.io/qrotor\n#'
    txt.edit.insert_at(filepath, file_comment, 0)
    print(f'Energy eigenvalues saved to {filepath}')
    return df


def save_splittings(
    systems:list,
    comment:str='',
    filepath:str='splittings.csv',
    ) -> pd.DataFrame:
    """Save the tunnel splitting energies for all `systems` to a splittings.csv file.

    Returns a Pandas Dataset with `System.comment` columns and `System.splittings` values.

    The output file can be changed with `filepath`,
    or set to null to avoid saving the dataset.
    A `comment` can be included at the top of the file.
    Note that `System.comment` must not include commas (`,`).
    Different splitting lengths across systems are allowed - missing values will be NaN.
    """
    as_list(systems)
    version = systems[0].version
    tunnelling_E = {}
    # Find max length of splittings
    max_len = max(len(s.splittings) for s in systems)
    for s in systems:  # Pad shorter splittings with NaN
        padded_splittings = s.splittings + [float('nan')] * (max_len - len(s.splittings))
        tunnelling_E[s.comment] = padded_splittings
    df = pd.DataFrame(tunnelling_E)
    if not filepath:
        return df
    # Else save to file
    df.to_csv(filepath, sep=',', index=False)
    # Include a comment at the top of the file 
    file_comment = f'# {comment}\n' if comment else f''
    file_comment += f'# Tunnel splitting energies\n'
    file_comment += f'# Calculated with QRotor {version}\n'
    file_comment += f'# https://pablogila.github.io/qrotor\n#'
    txt.edit.insert_at(filepath, file_comment, 0)
    print(f'Tunnel splitting energies saved to {filepath}')
    return df


def get_energies(systems:list) -> list:
    """Get a list with all lists of eigenvalues from all systems.

    If no eigenvalues are present for a particular system, appends None.
    """
    as_list(systems)
    energies = []
    for i in systems:
        if all(i.eigenvalues):
            energies.append(i.eigenvalues)
        else:
            energies.append(None)
    return energies


def get_gridsizes(systems:list) -> list:
    """Get a list with all gridsize values.

    If no gridsize value is present for a particular system, appends None.
    """
    as_list(systems)
    gridsizes = []
    for i in systems:
        if i.gridsize:
            gridsizes.append(i.gridsize)
        elif any(i.potential_values):
            gridsizes.append(len(i.potential_values))
        else:
            gridsizes.append(None)
    return gridsizes


def get_runtimes(systems:list) -> list:
    """Returns a list with all runtime values.
    
    If no runtime value is present for a particular system, appends None.
    """
    as_list(systems)
    runtimes = []
    for i in systems:
        if i.runtime:
            runtimes.append(i.runtime)
        else:
            runtimes.append(None)
    return runtimes


def get_groups(systems:list) -> list:
    """Returns a list with all `System.group` values."""
    as_list(systems)
    groups = []
    for i in systems:
        if i.group not in groups:
            groups.append(i.group)
    return groups


def get_ideal_E(E_level:int) -> int:
    """Calculates the ideal energy for a specified `E_level`.

    To be used in convergence tests with `potential_name = 'zero'`.
    """
    real_E_level = None
    if E_level % 2 == 0:
        real_E_level = E_level / 2
    else:
        real_E_level = (E_level + 1) / 2
    ideal_E = int(real_E_level ** 2)
    return ideal_E


def sort_by_gridsize(systems:list) -> list:
    """Sorts a list of System objects by `System.gridsize`."""
    as_list(systems)
    systems = sorted(systems, key=lambda sys: sys.gridsize)
    return systems


def reduce_size(systems:list) -> list:
    """Discard data that takes too much space.

    Removes eigenvectors, potential values and grids,
    for all System values inside the `systems` list.
    """
    as_list(systems)
    for dataset in systems:
        dataset = dataset.reduce_size()
    return systems


def summary(systems, verbose:bool=False) -> None:
    """Print a summary of a System or list of Systems.
    
    Print extra info with `verbose=True`
    """
    print('--------------------')
    systems = as_list(systems)
    for system in systems:
        dictionary = system.summary()
        if verbose:
            for key, value in dictionary.items():
                print(f'{key:<24}', value)
        else:
            eigenvalues = system.eigenvalues if any(system.eigenvalues) else []
            extra = ''
            if len(system.eigenvalues) > 6:
                eigenvalues = eigenvalues[:6]
                extra = '...'
            print('comment     ' + str(system.comment))
            print('B           ' + str(system.B))
            print('eigenvalues ' + str([float(round(e, 4)) for e in eigenvalues]) + extra)
            print('version     ' + str(system.version))
        print('--------------------')
    return None

