"""
# Description

This module contains common classes for QRotor calculations.


# Index

| | |
| --- | --- |
| `QSys` | Quantum system, with all the data for a single calculation |
| `QExp` | Quantum experiment, contains several `QSys` objects |

---
"""


import numpy as np
from copy import deepcopy
from .constants import *
import aton


class QSys:
    """Quantum system, contains all the data for a single calculation, with both inputs and outputs."""
    def __init__(
            self,
            comment: str = None,
            group: str = 'CH3',
            E_levels: int = 5,
            units = None,               ################ TODO CHECK THAT THIS WORKS. previously = []
            correct_potential_offset: bool = True,
            save_eigenvectors: bool = False,
            gridsize: int = None,
            grid = None,
            potential_name: str = None,
            potential_constants: list = None,
            potential_values = None,
            ):
        ## Technical
        self.comment: str = comment
        """Custom comment for the dataset."""
        self.group: str = group
        """Chemical group, methyl or amine: `'CH3'`, `'CD3'`, `'NH3'`, `'ND3'`."""
        self.set_group(group)  # Normalise the group name, and set the value of B
        self.E_levels: int = E_levels
        """Number of energy levels to be studied."""
        self.units = units
        """List containing the units in use, e.g. ['meV']."""     #############  TODO remove the need for a list
        self.correct_potential_offset: bool = correct_potential_offset
        """Correct the potential offset as `V - min(V)` or not."""
        self.save_eigenvectors: bool = save_eigenvectors
        """Save or not the eigenvectors. Final file size will be bigger."""
        ## Potential
        self.gridsize: int = gridsize
        """Number of points in the grid."""
        self.grid = grid
        """The grid with the points to be used in the calculation. Can be set automatically over $2 \\Pi$ with `System.set_grid()`."""
        if not B:
            B = self.B
        self.B: float = B
        """Rotational inertia, as in $B=\\frac{\\hbar^2}{2I}."""
        self.potential_name: str = potential_name
        """Name of the desired potential: `'zero'`, `'titov2023'`, `'test'`...
        If empty or unrecognised, the custom potential values inside `QSys.potential_values` will be used. 
        """
        self.potential_constants: list = potential_constants
        """List of constants to be used in the calculation of the potential energy, in the `qrotor.potential` module."""
        self.potential_values = potential_values
        """Numpy array with the potential values for each point in the grid.
        Can be calculated with a function available in the `qrotor.potential` module,
        or loaded externally with the `qrotor.potential.load()` function.
        """
        self.potential_offset: float = None
        """`min(V)` before offset correction when `correct_potential_offset=True`"""
        self.potential_min: float = None
        """`min(V)`"""
        self.potential_max: float = None
        """`max(V)`"""
        self.potential_max_B: float = None
        """Reduced `potential_max`, in units of B."""
        # Energies
        self.eigenvalues = None
        """Calculated eigenvalues of the system."""
        self.eigenvalues_B = None
        """Reduced `eigenvalues`, in units of B."""
        self.eigenvectors = None
        """Eigenvectors, if `save_eigenvectors` is True. Beware of the file size."""
        self.energy_barrier: float = None
        """`max(V) - min(eigenvalues)`"""
        self.first_transition: float = None
        """eigenvalues[1] - eigenvalues[0]"""
        self.runtime: float = None
        """Time taken to solve the eigenvalues."""

    def summary(self):
        return {
            'comment': self.comment,
            'runtime': self.runtime,
            'group': self.gropu,
            'gridsize': self.gridsize,
            'B': self.B,
            'potential_name': self.potential_name,
            'potential_constants': self.potential_constants.tolist() if isinstance(self.potential_constants, np.ndarray) else self.potential_constants,
            'potential_offset': self.corrected_potential_offset,
            'potential_min': self.potential_min,
            'potential_max': self.potential_max,
            'potential_max / B': self.potential_max_B,
            'eigenvalues': self.eigenvalues.tolist() if isinstance(self.eigenvalues, np.ndarray) else self.eigenvalues,
            'eigenvalues / B': self.eigenvalues_B.tolist() if isinstance(self.eigenvalues_B, np.ndarray) else self.eigenvalues_B,
            'energy_barrier': self.energy_barrier,
            'first_transition': self.first_transition,
        }

    def set_grid(self, gridsize:int=None):
        """Sets the `QSys.grid` to the specified `gridsize`."""
        if gridsize is not None:
            self.gridsize = gridsize
        if self.gridsize is None:
            raise ValueError('QSys.gridsize is not set yet!.')
        self.grid = np.linspace(0, 2*np.pi, self.gridsize)
        return self
    
    def set_group(self, group:str=None, B:float=None):
        """Normalise `QSys.group` name, and set `QSys.B` based on it."""
        for name in aton.st.alias.chemical['CH3']:
            if group.lower() == name:
                self.group = 'CH3'
                if not B:
                    B = B_CH
                self.B = B
                return self
        for name in aton.st.alias.chemical['CD3']:
            if group.lower() == name:
                self.group = 'CD3'
                if not B:
                    B = B_CD
                self.B = B
                return self
        for name in aton.st.alias.chemical['NH3']:
            if group.lower() == name:
                self.group = 'NH3'
                if not B:
                    B = B_NH
                self.B = B
                return self
        for name in aton.st.alias.chemical['ND3']:
            if group.lower() == name:
                self.group = 'ND3'
                if not B:
                    B = B_ND
                self.B = B
                return self
        self.group = group  # No match was found
        return self


class QExp:
    def __init__(self,
                 comment: str = None,
                 systems: list = [],
                 plotting: aton.spx.Plotting = None,
                 ):
        self.version = version                     ###########################  TODO __version__ once in ATON
        """Version of the package used to generate the data."""
        self.comment: str = comment
        """Custom comment for the dataset."""
        if isinstance(systems, QSys):
            systems = [systems]
        self.systems = systems
        """List containing the calculated `QSys` objects."""
        self.plotting: aton.spx.Plotting = plotting
        """`Aton.spx.classes.Plotting` object."""

    def add(self, *args):
        """Adds more systems to `self.systems` from the introduced `QSys` or `QExp` objects."""
        for value in args:
            if isinstance(value, QExp):
                self.systems.extend(value.systems)
                self.version = value.version if len(self.systems) == 0 else self.version
                self.comment = value.comment if self.comment is None else self.comment
                self.plotting = value.plotting if self.plotting is None else self.plotting
            elif isinstance(value, QSys):
                self.systems.append(value)
            else:
                raise TypeError(f'QExp.add() can only add QExp and/or QSys objects, not {type(value)}.')

    def get_energies(self):
        """Returns a list with all `QSys.eigenvalues` values."""
        energies = []
        for i in self.systems:
            if all(i.eigenvalues):
                energies.append(i.eigenvalues)
            else:
                energies.append(None)
        return energies

    def get_gridsizes(self):
        """Returns a list with all `QSys.gridsize` values."""
        gridsizes = []
        for i in self.systems:
            if i.gridsize:
                gridsizes.append(i.gridsize)
            else:
                gridsizes.append(None)
        return gridsizes

    def get_runtimes(self):
        """Returns a list with all `QSys.runtime` values."""
        runtimes = []
        for i in self.systems:
            if i.runtime:
                runtimes.append(i.runtime)
            else:
                runtimes.append(None)
        return runtimes

    def get_gropus(self):
        """Returns a list with all `QSys.group` values."""
        groups = []
        for i in self.systems:
            if i.group not in groups:
                groups.append(i.group)
        return groups

    def sort_by_potential_values(self):
        """Returns the `QExp` object, sorted by `QSys.potential_values`."""
        grouped_data = self.group_by_potential_values()
        data = QExp(
            version = self.version,
            comment = self.comment,
            plotting = self.plotting,
        )
        for dataset in grouped_data:
            data.add(dataset)
        return data

    def group_by_potential_values(self):
        """Returns an array of grouped `QExp` objects with the same `QSys.potential_values`."""
        print('Grouping Experiment by potential_values...')
        grouped_data = []
        for system in self.systems:
            data = QExp()
            data.comment = self.comment
            data.systems.append(system)
            new_group = True
            for data_i in grouped_data:
                if np.array_equal(system.potential_values, data_i.systems[0].potential_values):
                    data_i.systems.append(system)
                    new_group = False
                    break
            if new_group:
                print('New potential_values found')
                grouped_data.append(data)
        return grouped_data

    def sort_by_gridsize(self):
        """Returns the same `QExp`, sorted by `QSys.gridsize`."""
        self.systems = sorted(self.systems, key=lambda sys: sys.gridsize)
        return self

    def get_ideal_E(self, E_level):
        """Calculates the ideal energy for a specified `E_level` for a convergence test. Only for 'zero' potential."""
        real_E_level = None
        if self.systems[0].potential_name == 'zero':
            if E_level % 2 == 0:
                real_E_level = E_level / 2
            else:
                real_E_level = (E_level + 1) / 2
            ideal_E = int(real_E_level ** 2)
            return ideal_E
        else:
            print("WARNING:  get_ideal_E() only valid for potential_name='zero'")
            return
    
    def discard_shit(self):
        """Discard data that takes too much space, like eigenvectors, potential values and grids."""
        for dataset in self.systems:
            dataset.eigenvectors = None
            dataset.potential_values = None
            dataset.grid = None
        return self

