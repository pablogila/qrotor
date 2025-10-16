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
| `save_summary()`     | Save a summary of some relevant parameters for all systems to a CSV |
| `get_energies()`     | Get the eigenvalues from all systems |
| `get_gridsizes()`    | Get all gridsizes |
| `get_runtimes()`     | Get all runtimes |
| `get_ideal_E()`      | Calculate the ideal energy for a specified level |
| `sort_by_gridsize()` | Sort systems by gridsize |
| `reduce_size()`      | Discard data that takes too much space |
| `summary()`          | Print a summary of a System or list of Systems |
| `list_tags()`        | Get a list with all system tags |
| `filter_tags()`      | Filter the systems with or without specific tags |

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
        filepath:str='qrotor_eigenvalues.csv',
        ) -> pd.DataFrame:
    """Save the energy eigenvalues for all `systems` to a qrotor_eigenvalues.csv file.

    Returns a Pandas Dataset with `System.comment` columns and `System.eigenvalues` values.

    The output file can be changed with `filepath`,
    or set to null to avoid saving the dataset.
    A `comment` can be included at the top of the file.
    Note that `System.comment` must not include commas (`,`).
    """
    systems = as_list(systems)
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
    file_comment = f'## {comment}\n' if comment else f''
    file_comment += f'# Energy eigenvalues\n'
    file_comment += f'# Calculated with QRotor {version}\n'
    file_comment += f'# https://pablogila.github.io/qrotor\n#'
    txt.edit.insert_at(filepath, file_comment, 0)
    print(f'Energy eigenvalues saved to {filepath}')
    return df


def save_splittings(
    systems:list,
    comment:str='',
    filepath:str='qrotor_splittings.csv',
    ) -> pd.DataFrame:
    """Save the tunnel splitting energies for all `systems` to a qrotor_splittings.csv file.

    Returns a Pandas Dataset with `System.comment` columns and `System.splittings` values.

    The output file can be changed with `filepath`,
    or set to null to avoid saving the dataset.
    A `comment` can be included at the top of the file.
    Note that `System.comment` must not include commas (`,`).
    Different splitting lengths across systems are allowed - missing values will be NaN.
    """
    systems = as_list(systems)
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
    file_comment = f'## {comment}\n' if comment else f''
    file_comment += f'# Tunnel splitting energies\n'
    file_comment += f'# Calculated with QRotor {version}\n'
    file_comment += f'# https://pablogila.github.io/qrotor\n#'
    txt.edit.insert_at(filepath, file_comment, 0)
    print(f'Tunnel splitting energies saved to {filepath}')
    return df


def save_summary(
    systems:list,
    comment:str='',
    filepath:str='qrotor_summary.csv',
    ) -> pd.DataFrame:
    """Save a summary for all `systems` to a qrotor_summary.csv file.

    Produces one row per System with the columns:
    `comment`, `ZPE`, `E_activation`, `potential_max`, `1st_splitting`,
    `1st_excitation`, `B`, `degeneracy`, `gridsize`.

    Set `filepath` to null to just return the DataFrame.
    """
    systems = as_list(systems)
    version = systems[0].version
    rows = []
    for s in systems:
        eigenvalues = getattr(s, 'eigenvalues', None)
        if eigenvalues is not None and len(eigenvalues) > 0:
            first_val = eigenvalues[0]
            zpe = float('nan') if first_val is None else first_val
        else:
            zpe = float('nan')
        splittings = getattr(s, 'splittings', None)
        if splittings is not None and len(splittings) > 0:
            first_splitting = float('nan') if splittings[0] is None else splittings[0]
        else:
            first_splitting = float('nan')
        excitations = getattr(s, 'excitations', None)
        if excitations is not None and len(excitations) > 0:
            first_excitation = float('nan') if excitations[0] is None else excitations[0]
        else:
            first_excitation = float('nan')
        system_comment = getattr(s, 'comment', None)
        E_activation = getattr(s, 'E_activation', None)
        B = getattr(s, 'B', None)
        tags = getattr(s, 'tags', None)
        deg = getattr(s, 'deg', None)
        gridsize = getattr(s, 'gridsize', None)
        potential_max = getattr(s, 'potential_max', None)
        # Each row contains the following:
        rows.append({
            'comment': system_comment,
            'ZPE': zpe,
            'E_activation': E_activation,
            'potential_max': potential_max,
            '1st_splitting': first_splitting,
            '1st_excitation': first_excitation,
            'B': B,
            'degeneracy': deg,
            'gridsize': gridsize,
            'tags': tags,
        })
    # Save to file or just return df
    df = pd.DataFrame(rows)
    if not filepath:
        return df
    df.to_csv(filepath, sep=',', index=False)
    # Include a comment at the top of the file
    file_comment = f'## {comment}\n' if comment else ''
    file_comment += '# Summary of systems\n'
    file_comment += f'# Calculated with QRotor {version}\n'
    file_comment += '# https://pablogila.github.io/qrotor\n#'
    txt.edit.insert_at(filepath, file_comment, 0)
    print(f'Summary saved to {filepath}')
    return df


def get_energies(systems:list) -> list:
    """Get a list with all lists of eigenvalues from all systems.

    If no eigenvalues are present for a particular system, appends None.
    """
    systems = as_list(systems)
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
    systems = as_list(systems)
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
    systems = as_list(systems)
    runtimes = []
    for i in systems:
        if i.runtime:
            runtimes.append(i.runtime)
        else:
            runtimes.append(None)
    return runtimes


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
    systems = as_list(systems)
    systems = sorted(systems, key=lambda sys: sys.gridsize)
    return systems


def reduce_size(systems:list) -> list:
    """Discard data that takes too much space.

    Removes eigenvectors, potential values and grids,
    for all System values inside the `systems` list.
    """
    systems = as_list(systems)
    for dataset in systems:
        dataset = dataset.reduce_size()
    return systems


def summary(
        systems,
        verbose:bool=False
        ) -> None:
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


def list_tags(systems:list) -> list:
    """Returns a list with all system tags."""
    systems = as_list(systems)
    tags = []
    for i in systems:
        # i.tags is guaranteed to exist and be a string (may be empty)
        system_tags = i.tags.split()
        for tag in system_tags:
            if tag not in tags:
                tags.append(tag)
    return tags


def filter_tags(
        systems:list,
        include:str='',
        exclude:str='',
        strict:bool=False,
        ) -> list:
    """Returns a filtered list of systems with or without specific tags.

    You can `include` or `exclude` any number of tags, separated by blank spaces.
    By default, the filters are triggered if any tag is found, i.e. *tag1 OR tag2*.
    Set `strict=True` to require all tags to match, i.e. *tag1 AND tag2*.
    """
    systems = as_list(systems)
    included_tags = include.split()
    excluded_tags = exclude.split()
    filtered_systems = []
    for i in systems:
        tags_found = list_tags(i)
        if excluded_tags:
            if strict and all(tag in tags_found for tag in excluded_tags):
                continue
            elif not strict and any(tag in tags_found for tag in excluded_tags):
                continue
        if included_tags:
            if strict and not all(tag in tags_found for tag in included_tags):
                continue
            elif not strict and not any(tag in tags_found for tag in included_tags):
                continue
        filtered_systems.append(i)
    return filtered_systems

