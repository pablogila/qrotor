'''
## Description

This module contains the common objects used in the QRotor package.

Short general description of the class methods used:
- `get_*`  ->  Returns a value from another value, e.g. get_B(atom_type) returns the rotational inertia.
- `set_*`  ->  Sets a value, e.g. set_grid() sets the grid from the gridsize.
- `to_*`   ->  Converts to whatever
- `from_*` ->  Converts from whatever

## Index

- `System`. Contains all the data for a single calculation.
- `Analysis`. Contains different parameters to analyze the data.
- `Data`. Contains a list of `System` objects, an `Analysis` object, and some plotting options as a [Maat plotting object](https://pablogila.github.io/Maat/maat/classes.html#Plotting).
'''


import numpy as np
from copy import deepcopy
import maat as mt
from .constants import *
# Get Maat from:
# https://github.com/pablogila/Maat


class System:
    '''Object containing all the data for a single calculation, with both inputs and outputs.'''
    def __init__(self,
                 comment: str = None,
                 E_levels: int = 5,
                 units = None, # CHECK THAT THIS WORKS. previously = []
                 atom_type: str = None,
                 correct_potential_offset: bool = True,
                 save_eigenvectors: bool = False,
                 gridsize: int = None,
                 grid = None,
                 B: float = None,
                 potential_name: str = None,
                 potential_constants: list = None
                 ):
        '''Input parameters can be set at initialization, or modified later.'''
        ## Technical
        self.comment: str = comment
        '''Custom comment for the dataset.'''
        self.E_levels: int = E_levels
        '''Number of energy levels to be studied.'''
        self.units = units
        '''List containing the units in use, e.g. ['meV'].'''
        self.atom_type: str = atom_type
        '''Generally `'H'` or `'D'`.'''
        self.correct_potential_offset: bool = correct_potential_offset
        '''Correct the potential offset as `V - min(V)` or not.'''
        self.save_eigenvectors: bool = save_eigenvectors
        '''Save or not the eigenvectors. Final file size will be bigger.'''
        ## Potential
        self.gridsize: int = gridsize
        '''Number of points in the grid.'''
        self.grid = grid
        '''The grid with the points to be used in the calculation. Can be set automatically over $2 \\Pi$ with `System.set_grid()`.'''
        self.B: float = B
        '''Rotational inertia, as in $B=\\frac{\\hbar^2}{2I}.'''
        self.potential_name: str = potential_name
        '''
        String with the name of the desired potential: `'zero'`, `'titov2023'`, `'test'`...
        If empty or unrecognised, the custom potential values inside `potential_values` will be used. 
        '''
        self.potential_constants: list = potential_constants
        '''List of constants to be used in the calculation of the potential energy, in the `qrotor.potentials` module.'''
        self.potential_values = None
        '''
        Numpy array with the potential values for each point in the grid.
        Can be calculated with a function available in the `qrotor.potentials` module,
        or loaded externally with the `qrotor.file.load_potential()` function.
        '''
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
            'atom_type': self.atom_type,
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


class Analysis:
    '''
    Analysis object containing the different parameters to analyze the data.
    '''
    def __init__(self,
                 E_level: int = 5,
                 E_diff: bool = False,
                 E_threshold: float = 1e-3,
                 ideal_E: float = None,
                 ):
        
        self.E_level: int = E_level
        '''Energy level to check in a convergence test. By default, it will be the higher calculated one.'''
        self.E_diff: bool = E_diff
        '''If True, in plot.convergence it will check the difference between ideal_E and the calculated one.'''
        self.E_threshold: float = E_threshold
        '''Energy Threshold for a convergence test.'''
        self.ideal_E: float = ideal_E
        '''Ideal energy level for a 'zero' potential, for comparison in a convergence test. Calculated automatically with Data.get_ideal_E()'''


class Data:
    def __init__(self,
                 comment: str = None,
                 plotting: mt.Plotting = None,
                 analysis: Analysis = None,
                 ):
        self.version = version
        '''Version of the QRotor package used to generate the data.'''
        self.comment: str = comment
        '''Custom comment for the dataset.'''
        self.system = []
        '''List containing the calculated System objects.'''
        self.plotting = plotting
        '''Maat plotting object. Check more options [here](https://pablogila.github.io/Maat/maat/classes.html#Plotting).'''
        self.analysis = analysis
        '''Analysis object containing the different parameters to analyze the data.'''


    def add(self, *args):
        for value in args:
            if isinstance(value, Data):
                self.system.extend(value.system)
                self.version = value.version if len(self.system) == 0 else self.version
                self.comment = value.comment if self.comment is None else self.comment
                self.plotting = value.plotting if self.plotting is None else self.plotting
                self.analysis = value.analysis if self.analysis is None else self.analysis
            elif isinstance(value, System):
                self.system.append(value)
            else:
                raise TypeError(f'Data.add() can only add Data and/or System objects, not {type(value)}.')


    def discard_shit(self):
        '''Discard data that takes too much space'''
        for dataset in self.system:
            dataset.eigenvectors = None
            dataset.potential_values = None
            dataset.grid = None
        return self


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


    def get_atom_types(self):
        atom_types = []
        for i in self.system:
            if i.atom_type not in atom_types:
                atom_types.append(i.atom_type)
        return atom_types


    def sort_by_potential_values(self):
        grouped_data = self.group_by_potential_values()
        data = Data()
        for dataset in grouped_data:
            data.add(dataset)
        return data


    def group_by_potential_values(self):
        '''Returns an array of grouped Data objects with the same potential_values'''
        print('Grouping Data by potential_values...')
        grouped_data = []
        for system in self.system:
            data = Data()
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


    def get_ideal_E(self):
        '''Only for 'zero' potential. Calculates the ideal energy level for a convergence test, from Data.Analysis.E_level'''
        real_E_level = None
        if self.plotting.check_E_level is None:
            raise ValueError("Data.Plotting.check_E_level not set.")
        if self.system[0].potential_name == 'zero':
            if self.plotting.check_E_level % 2 == 0:
                real_E_level = self.check_E_level / 2
            else:
                real_E_level = (self.check_E_level + 1) / 2
            self.plotting.ideal_E = int(real_E_level ** 2)
            return self.plotting.ideal_E
        else:
            print("WARNING:  get_ideal_E() only valid for potential_name='zero'")
            return
    
