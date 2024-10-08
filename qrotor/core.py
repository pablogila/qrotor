import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh
from scipy.interpolate import CubicSpline
from copy import deepcopy
import os
import gzip
import shutil
import json
import time
import maat as mt
# Get Maat from:
# https://github.com/pablogila/Maat


version = 'v3.0.0-dev2'


'''
Short description of the class methods used:
get_*:  Returns a value from another value, e.g. get_B(atom_type) returns the rotational inertia.
set_*:  Sets a value, e.g. set_grid() sets the grid from the gridsize.
'''


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
        self.grid = get_grid(gridsize) if grid is None else grid
        '''Grid, e.g. np.linspace(min, max, gridsize).'''
        self.B: float = get_B(atom_type) if B is None else B
        '''Rotational inertia.'''
        self.potential_name: str = potential_name
        '''str: 'zero', 'titov2023', 'test'...'''
        self.potential_constants: list = potential_constants
        self.potential_values = None
        self.potential_offset: float = None
        '''min(V) if the potential is corrected as V - min(V)'''
        self.min_potential: float = None
        self.max_potential: float = None
        self.max_potential_B: float = None
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
            'min_potential': self.min_potential,
            'max_potential': self.max_potential,
            'max_potential_B': self.max_potential_B,
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
            'min_potential': self.min_potential,
            'max_potential': self.max_potential,
            'max_potential / B': self.max_potential_B,
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


    def get_B(atom_type:str):
        '''Returns the rotational inertia of the atom_type.'''
        if atom_type in  ['H','h', 'H1', 'h1', 'hydrogen', 'Hydrogen', 'HYDROGEN']:
            return mt.constants.B_Hydrogen
        elif atom_type in ['D','d', 'H2', 'h2', 'deuterium', 'Deuterium', 'DEUTERIUM']:
            return mt.constants.B_Deuterium
        else:
            return None
    def set_B(self):
        self.B = get_B(self.atom_type)
        return self


    def get_grid(gridsize:int):
        if gridsize is None:
            return None
        return np.linspace(0, 2*np.pi, gridsize)
    def set_grid(self):
        self.grid = get_grid(self.gridsize)
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
                self.version = value.version if len(self.set) == 0 else self.version
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
                self.set.append(value)
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
        for i in self.solutions:
            if i.runtime:
                runtimes.append(i.runtime)
            else:
                runtimes.append(None)
        return runtimes


    def get_atom_types(self):
        atom_types = []
        for i in self.variables:
            if i.atom_type not in atom_types:
                atom_types.append(i.atom_type)
        return atom_types



########  ME LLEGO POR AQUÍ ################################################################


    def sort_by_potential_values(self):
        grouped_data = self.group_by_potential_values()
        data = Data()
        for dataset in grouped_data:
            data.add(dataset)
        return data


    def group_by_potential_values(self):
        '''Returns an array of grouped Data objects with the same potential_values'''
        '''Orders consecutively data with the same potential_values'''
        print('Grouping Data by potential_values...')
        grouped_data = []
        for new_variables, new_solutions in zip(self.variables, self.solutions):
            new_data = Data()
            new_data.comment = self.comment
            new_data.variables.append(new_variables)
            new_data.solutions.append(new_solutions)
            can_be_grouped = True
            for group in grouped_data:
                can_be_grouped = True
                for variable in group.variables:
                    if not np.array_equal(new_variables.potential_values, variable.potential_values):
                        can_be_grouped = False
                        break
                if can_be_grouped:
                    group.variables.append(new_variables)
                    group.solutions.append(new_solutions)
                    break
            if can_be_grouped == True:
                print('New potential_values found')
                grouped_data.append(new_data)
        return grouped_data


    def group_by_potential_and_atoms(self):
        '''Returns an array of grouped Data objects with the same potential_values and different atom_type'''
        grouped_data = []
        for new_variables, new_solutions in zip(self.variables, self.solutions):
            new_data = Data()
            new_data.comment = self.comment
            new_data.variables.append(new_variables)
            new_data.solutions.append(new_solutions)
            has_been_grouped = False
            for group in grouped_data:
                can_be_grouped = True
                for variable in group.variables:
                    if not np.array_equal(new_variables.potential_values, variable.potential_values) or (new_variables.atom_type == variable.atom_type):
                        can_be_grouped = False
                        break
                if can_be_grouped:
                    group.variables.append(new_variables)
                    group.solutions.append(new_solutions)
                    has_been_grouped = True
                    break
            if not has_been_grouped:
                grouped_data.append(new_data)
        return grouped_data


    def sort_by_gridsize(self):
        variables = self.variables
        solutions = self.solutions
        paired_data = list(zip(variables, solutions))
        paired_data.sort(key=lambda pair: pair[0].gridsize)
        self.variables, self.solutions = zip(*paired_data)
        self.variables = list(self.variables)
        self.solutions = list(self.solutions)
        return self


    def sort_by_atom_type(self, ordering:list=['H', 'D']):
        '''Sorts the data by atom_type, according to a given ordering list, e.g. ['H', 'D'].'''
        variables = self.variables
        solutions = self.solutions
        paired_data = list(zip(variables, solutions))
        paired_data.sort(key=lambda pair: ordering.index(pair[0].atom_type))
        self.variables, self.solutions = zip(*paired_data)
        self.variables = list(self.variables)
        self.solutions = list(self.solutions)
        return self





    


    def get_ideal_E(self):
        '''Only for 'zero' potential. Calculates the ideal energy level for a convergence test, from check_E_level.'''
        real_E_level = None
        if self.check_E_level is None:
            print("WARNING: get_ideal_E() requires check_E_level to be set.")
            return
        if self.variables[0].potential_name == 'zero':
            if self.check_E_level % 2 == 0:
                real_E_level = self.check_E_level / 2
            else:
                real_E_level = (self.check_E_level + 1) / 2
            self.ideal_E = int(real_E_level ** 2)
            return self.ideal_E
        else:
            print("WARNING: get_ideal_E() only valid for potential_name='zero'")
            return
    
