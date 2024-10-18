'''
Common classes used in the QRotor package.

Short general description of the class methods used:
- `get_*`  ->  Returns a value from another value, e.g. get_B(atom_type) returns the rotational inertia.
- `set_*`  ->  Sets a value, e.g. set_grid() sets the grid from the gridsize.
- `to_*`   ->  Converts to whatever
- `from_*` ->  Converts from whatever
'''


import numpy as np
from copy import deepcopy
import maat as mt
# Get Maat from:
# https://github.com/pablogila/Maat


class System:
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
        ## Technical
        self.comment: str = comment
        self.E_levels: int = E_levels
        '''Number of energy levels to be studied.'''
        self.units = units
        '''List containing the units in use, e.g. ['meV'].'''
        self.atom_type: str = atom_type
        '''Generally 'H' or 'D'.'''
        self.correct_potential_offset: bool = correct_potential_offset
        '''If true, do not correct the potential offset.'''
        self.save_eigenvectors: bool = save_eigenvectors
        '''Save or not the eigenvectors. Final file size will be bigger.'''
        ## Potential
        self.gridsize: int = gridsize
        self.grid = grid
        '''Grid, e.g. np.linspace(min, max, gridsize).'''
        self.B: float = B
        '''Rotational inertia.'''
        self.potential_name: str = potential_name
        '''str: 'zero', 'titov2023', 'test'...'''
        self.potential_constants: list = potential_constants
        self.potential_values = None
        self.potential_offset: float = None
        '''min(V) if the potential is corrected as V - min(V)'''
        self.potential_min: float = None
        self.potential_max: float = None
        self.potential_max_B: float = None
        '''Reduced max_potential, in units of B.'''
        # Energies
        self.eigenvalues = None
        self.eigenvalues_B = None
        '''Reduced eigenvalues, in units of B.'''
        self.eigenvectors = None
        '''Eigenvectors, if save_eigenvectors is True. Beware of the file size.'''
        self.energy_barrier: float = None
        '''max(V) - min(eigenvalues)'''
        self.first_transition: float = None
        '''eigenvalues[1] - eigenvalues[0]'''
        self.runtime: float = None
        '''Time taken to solve the eigenvalues.'''


    def to_dict(self):
        return {
            'comment': self.comment,
            'E_levels': self.E_levels,
            'units': self.units,
            'atom_type': self.atom_type,
            'correct_potential_offset': self.correct_potential_offset,
            'save_eigenvectors': self.save_eigenvectors,
            'gridsize': self.gridsize,
            'grid': self.grid.tolist() if isinstance(self.grid, np.ndarray) else self.grid,
            'B': self.B,
            'potential_name': self.potential_name,
            'potential_constants': self.potential_constants.tolist() if isinstance(self.potential_constants, np.ndarray) else self.potential_constants,
            'potential_values': self.potential_values.tolist() if isinstance(self.potential_values, np.ndarray) else self.potential_values,
            'potential_offset': self.corrected_potential_offset,
            'potential_min': self.potential_min,
            'potential_max': self.potential_max,
            'potential_max_B': self.potential_max_B,
            # Energies
            'eigenvalues': self.eigenvalues.tolist() if isinstance(self.eigenvalues, np.ndarray) else self.eigenvalues,
            'eigenvalues_B': self.eigenvalues_B.tolist() if isinstance(self.eigenvalues_B, np.ndarray) else self.eigenvalues_B,
            'eigenvectors': self.eigenvectors.tolist() if isinstance(self.eigenvectors, np.ndarray) else self.eigenvectors,
            'energy_barrier': self.energy_barrier,
            'first_transition': self.first_transition,
            'runtime': self.runtime,
        }


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


    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.__dict__.update(data)
        obj.grid = np.array(data['grid']) if 'grid' in data else None
        obj.potential_constants = np.array(data['potential_constants']) if 'potential_constants' in data else None
        obj.potential_values = np.array(data['potential_values']) if 'potential_values' in data else None
        obj.eigenvalues = np.array(data['eigenvalues']) if 'eigenvalues' in data else None
        obj.eigenvalues_B = np.array(data['eigenvalues_B']) if 'eigenvalues_B' in data else None
        obj.eigenvectors = np.array(data['eigenvectors']) if 'eigenvectors' in data else None
        return obj


    def set_grid(self, gridsize:int=None):
        if gridsize is not None:
            self.gridsize = gridsize
        if self.gridsize is None:
            raise ValueError('System.gridsize not set.')
        self.grid = np.linspace(0, 2*np.pi, self.gridsize)
        return self


class Plotting:
    def __init__(self,
                 title: str = None,
                 plot_label = None,
                 plot_label_position: tuple = None,
                 separate_plots: bool = None,
                 check_E_level: int = None,
                 check_E_diff: bool = None,
                 check_E_threshold: float = None,
                 ideal_E: float = None
                 ):
        self.title: str = title
        self.plot_label = plot_label
        '''Can be a bool, or a str for a label title.'''
        self.plot_label_position: tuple = plot_label_position
        '''Label position. (position_x, position_y, alignment_v, alignment_h)'''
        self.separate_plots: bool = separate_plots
        '''Do not merge plots with different atoms in the same figure.'''
        # Convergence tests
        self.check_E_level: int = check_E_level
        '''Energy level to check in a convergence test. By default, it will be the higher calculated one.'''
        self.check_E_diff: bool = check_E_diff
        '''If True, in plot.convergence it will check the difference between ideal_E and the calculated one.'''
        self.check_E_threshold: float = check_E_threshold
        '''Energy Threshold for a convergence test.'''
        self.ideal_E: float = ideal_E
        '''Ideal energy level for a 'zero' potential, for comparison in a convergence test. Calculated automatically with Data.get_ideal_E()'''


    def to_dict(self):
        return {
            'plot_label': self.plot_label,
            'plot_label_position': self.plot_label_position,
            'separate_plots': self.separate_plots,
            'check_E_level': self.check_E_level,
            'check_E_diff': self.check_E_diff,
            'check_E_threshold': self.check_E_threshold,
            'ideal_E': self.ideal_E
        }


    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.__dict__.update(data)
        return obj


class Data:
    def __init__(self,
                 comment: str = None,
                 ):
        self.version = version
        self.comment: str = comment
        self.system = []
        '''List of System objects.'''
        self.plotting = Plotting()


    def to_dict(self):
        return {
            'version': self.version,
            'comment': self.comment,
            'system': [s.to_dict() for s in self.system],
            'plotting': self.plotting.to_dict()
        }


    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.__dict__.update(data)
        obj.system = [System.from_dict(s) for s in data['system']]
        obj.plotting = Plotting.from_dict(data['plotting'])
        return obj


    def add(self, *args):
        for value in args:
            if isinstance(value, Data):
                self.system.extend(value.system)
                self.version = value.version if len(self.system) == 0 else self.version
                self.comment = value.comment if self.comment is None else self.comment
                self.plotting.title = value.plotting.title if self.plotting.title is None else self.plotting.title
                self.plotting.plot_label = value.plotting.plot_label if self.plotting.plot_label is None else self.plotting.plot_label
                self.plotting.plot_label_position = value.plotting.plot_label_position if self.plotting.plot_label_position is None else self.plotting.plot_label_position
                self.plotting.separate_plots = value.plotting.separate_plots if self.plotting.separate_plots is None else self.plotting.separate_plots
                self.plotting.check_E_level = value.plotting.check_E_level if self.plotting.check_E_level is None else self.plotting.check_E_level
                self.plotting.check_E_diff = value.plotting.check_E_diff if self.plotting.check_E_diff is None else self.plotting.check_E_diff
                self.plotting.check_E_threshold = value.plotting.check_E_threshold if self.plotting.check_E_threshold is None else self.plotting.check_E_threshold
                self.plotting.ideal_E = value.plotting.ideal_E if self.plotting.ideal_E is None else self.plotting.ideal_E
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
        '''Only for 'zero' potential. Calculates the ideal energy level for a convergence test, from Data.Plotting.check_E_level'''
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
    
