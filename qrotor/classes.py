"""
# Description

This module contains common classes for QRotor calculations.


# Index

| | |
| --- | --- |
| `System`     | Contains all the data for a single calculation |
| `Experiment` | Container for several `System` objects, with specific methods |

---
"""


import numpy as np
from copy import deepcopy
from .constants import *
import aton


class System:
    """Contains all the data for a single calculation, with both inputs and outputs."""
    def __init__(
            self,
            comment: str = None,
            E_levels: int = 5,
            units = None,               ################ TODO CHECK THAT THIS WORKS. previously = []
            element: str = None,
            correct_potential_offset: bool = True,
            save_eigenvectors: bool = False,
            gridsize: int = None,
            grid = None,
            B: float = None,
            potential_name: str = None,
            potential_constants: list = None
            ):
        ## Technical
        self.comment: str = comment
        """Custom comment for the dataset."""
        self.E_levels: int = E_levels
        """Number of energy levels to be studied."""
        self.units = units
        """List containing the units in use, e.g. ['meV']."""     #############  TODO remove the need for a list
        self.element: str = element
        """Generally `'H'` or `'D'`."""
        self.correct_potential_offset: bool = correct_potential_offset
        """Correct the potential offset as `V - min(V)` or not."""
        self.save_eigenvectors: bool = save_eigenvectors
        """Save or not the eigenvectors. Final file size will be bigger."""
        ## Potential
        self.gridsize: int = gridsize
        """Number of points in the grid."""
        self.grid = grid
        """The grid with the points to be used in the calculation. Can be set automatically over $2 \\Pi$ with `System.set_grid()`."""
        self.B: float = B
        """Rotational inertia, as in $B=\\frac{\\hbar^2}{2I}."""
        self.potential_name: str = potential_name
        """Name of the desired potential: `'zero'`, `'titov2023'`, `'test'`...

        If empty or unrecognised, the custom potential values inside `potential_values` will be used. 
        """
        self.potential_constants: list = potential_constants
        """List of constants to be used in the calculation of the potential energy, in the `qrotor.potential` module."""
        self.potential_values = None
        """Numpy array with the potential values for each point in the grid.

        Can be calculated with a function available in the `qrotor.potential` module,
        or loaded externally with the `qrotor.load_potential()` function.
        """
        self.potential_offset: float = None
        '''`min(V)` before offset correction when `correct_potential_offset=True`'''
        self.potential_min: float = None
        '''`min(V)`'''
        self.potential_max: float = None
        '''`max(V)`'''
        self.potential_max_B: float = None
        '''Reduced `potential_max`, in units of B.'''
        # Energies
        self.eigenvalues = None
        '''Calculated eigenvalues of the system.'''
        self.eigenvalues_B = None
        '''Reduced `eigenvalues`, in units of B.'''
        self.eigenvectors = None
        '''Eigenvectors, if `save_eigenvectors` is True. Beware of the file size.'''
        self.energy_barrier: float = None
        '''`max(V) - min(eigenvalues)`'''
        self.first_transition: float = None
        '''eigenvalues[1] - eigenvalues[0]'''
        self.runtime: float = None
        '''Time taken to solve the eigenvalues.'''

    def summary(self):
        return {
            'comment': self.comment,
            'runtime': self.runtime,
            'element': self.element,
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
        if gridsize is not None:
            self.gridsize = gridsize
        if self.gridsize is None:
            raise ValueError('System.gridsize is not set yet!.')
        self.grid = np.linspace(0, 2*np.pi, self.gridsize)
        return self


class Experiment:
    def __init__(self,
                 comment: str = None,
                 plotting: mt.Plotting = None,
                 ):
        self.version = version
        """Version of the package used to generate the data."""
        self.comment: str = comment
        """Custom comment for the dataset."""
        self.system = []
        """List containing the calculated `System` objects."""
        self.plotting: aton.spx.classes.Plotting = plotting
        """`Aton.spx.classes.Plotting` object."""

    def add(self, *args):
        for value in args:
            if isinstance(value, Experiment):
                self.system.extend(value.system)
                self.version = value.version if len(self.system) == 0 else self.version
                self.comment = value.comment if self.comment is None else self.comment
                self.plotting = value.plotting if self.plotting is None else self.plotting
            elif isinstance(value, System):
                self.system.append(value)
            else:
                raise TypeError(f'Experiment.add() can only add Experiment and/or System objects, not {type(value)}.')

    def get_energies(self):
        energies = []
        for i in self.system:
            if all(i.eigenvalues):
                energies.append(i.eigenvalues)
            else:
                energies.append(None)
        return energies

    def get_gridsizes(self):
        gridsizes = []
        for i in self.system:
            if i.gridsize:
                gridsizes.append(i.gridsize)
            else:
                gridsizes.append(None)
        return gridsizes

    def get_runtimes(self):
        runtimes = []
        for i in self.system:
            if i.runtime:
                runtimes.append(i.runtime)
            else:
                runtimes.append(None)
        return runtimes

    def get_elements(self):
        elements = []
        for i in self.system:
            if i.element not in elements:
                elements.append(i.element)
        return elements

    def sort_by_potential_values(self):
        grouped_data = self.group_by_potential_values()
        data = Experiment()
        for dataset in grouped_data:
            data.add(dataset)
        return data

    def group_by_potential_values(self):
        '''Returns an array of grouped Experiment objects with the same potential_values'''
        print('Grouping Experiment by potential_values...')
        grouped_data = []
        for system in self.system:
            data = Experiment()
            data.comment = self.comment
            data.system.append(system)
            new_group = True
            for data_i in grouped_data:
                if np.array_equal(system.potential_values, data_i.system[0].potential_values):
                    data_i.system.append(system)
                    new_group = False
                    break
            if new_group:
                print('New potential_values found')
                grouped_data.append(data)
        return grouped_data

    def sort_by_gridsize(self):
        self.system = sorted(self.system, key=lambda sys: sys.gridsize)
        return self

    def get_ideal_E(self, E_level):
        """Calculates the ideal energy for a specified `E_level` for a convergence test. Only for 'zero' potential."""
        real_E_level = None
        if self.system[0].potential_name == 'zero':
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
        '''Discard data that takes too much space'''
        for dataset in self.system:
            dataset.eigenvectors = None
            dataset.potential_values = None
            dataset.grid = None
        return self

