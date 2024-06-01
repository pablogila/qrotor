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


version = 'vQR.2024.06.02.1200'


class Variables:
    def __init__(self):
        self.comment = None
        self.atom_type = None
        '''Generally 'H' or 'D'.'''
        self.searched_E_levels = 5
        '''Number of energy levels to search for.'''
        self.units = []
        '''List containing the units in use, e.g. ['meV'].'''

        self.gridsize = None
        self.grid = None
        '''Grid, e.g. np.linspace(min, max, gridsize).'''
        self.B = None
        '''Inertia.'''

        self.potential_name = None
        '''str: 'zero', 'titov2023', 'test'...'''
        self.potential_constants = None
        self.potential_values = None
        #self.set_of_constants = None
        #'''DEPRECATED.'''

        self.leave_potential_offset = None
        '''If true, do not correct the potential offset.'''
        self.corrected_potential_offset = None
        '''Calculated offset potential.'''


    def to_dict(self):
        return {
            'comment': self.comment,
            'atom_type': self.atom_type,
            'searched_E_levels': self.searched_E_levels,
            'units': self.units,

            'gridsize': self.gridsize,
            'grid': self.grid.tolist() if isinstance(self.grid, np.ndarray) else self.grid,
            'B': self.B,

            'potential_name': self.potential_name,
            'potential_constants': self.potential_constants.tolist() if isinstance(self.potential_constants, np.ndarray) else self.potential_constants,
            #'set_of_constants': self.set_of_constants.tolist() if isinstance(self.set_of_constants, np.ndarray) else self.set_of_constants,
            'potential_values': self.potential_values.tolist() if isinstance(self.potential_values, np.ndarray) else self.potential_values,
            
            'leave_potential_offset': self.leave_potential_offset,
            'corrected_potential_offset': self.corrected_potential_offset,
        }


    def summary(self):
        summary_dict = {
            'comment': self.comment,
            'atom_type': self.atom_type,
            'gridsize': self.gridsize,
            'B': self.B,
            'potential_name': self.potential_name,
            'potential_constants': self.potential_constants.tolist() if isinstance(self.potential_constants, np.ndarray) else self.potential_constants,
            'corrected_potential_offset': self.corrected_potential_offset,
        }
        return summary_dict


    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.__dict__.update(data)
        obj.grid = np.array(obj.grid)
        obj.potential_values = np.array(obj.potential_values)
        return obj


class Solutions:
    def __init__(self):
        self.comment = None
        self.runtime = None

        self.max_potential = None
        self.min_potential = None

        self.eigenvalues = None
        self.eigenvectors = None
        self.energy_barrier = None
        self.first_transition = None


    def to_dict(self):
        return {
            'comment': self.comment,
            'runtime': self.runtime,

            'max_potential': self.max_potential,
            'min_potential': self.min_potential,

            'eigenvalues': self.eigenvalues.tolist() if isinstance(self.eigenvalues, np.ndarray) else self.eigenvalues,
            'eigenvectors': self.eigenvectors.tolist() if isinstance(self.eigenvectors, np.ndarray) else self.eigenvectors,
            'energy_barrier': self.energy_barrier,
            'first_transition': self.first_transition,
        }


    def summary(self):
        summary_dict = {
            'comment': self.comment,

            'eigenvalues': self.eigenvalues,
            'energy_barrier': self.energy_barrier,
            'first_transition': self.first_transition,

            'max_potential': self.max_potential,
            'min_potential': self.min_potential,

            'runtime': self.runtime,
        }
        return summary_dict


    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.__dict__.update(data)
        # obj.eigenvalues = np.array(obj.eigenvalues) if isinstance(obj.eigenvalues, list) else obj.eigenvalues
        # obj.eigenvalues = np.array(obj.eigenvalues)
        # obj.eigenvectors = np.array(obj.eigenvectors) if isinstance(obj.eigenvectors, list) else obj.eigenvectors
        obj.eigenvectors = np.array(obj.eigenvectors)
        return obj


class Data:
    def __init__(self):

        self.version = version
        self.comment = None

        self.variables = []
        self.solutions = []

        # Plotting
        self.write_summary = None
        '''Write an additional .txt file with a summary of the calculations. Set it to False to disable it.'''
        self.separate_plots = None
        '''Do not merge plots with different atoms in the same figure.'''
        self.plot_label = None
        '''Can be a bool, or a str for a label title.'''
        self.plot_label_position = None
        '''Label position. (position_x, position_y, alignment_v, alignment_h)'''
        
        # Convergence tests
        self.check_E_level = None
        '''Energy level to check in a convergence test. By default, it will be the higher calculated one.'''
        self.check_E_diff = None
        '''If True, in plot.convergence it will check the difference between ideal_E and the calculated one.'''
        self.check_E_threshold = None
        '''Energy Threshold for a convergence test.'''
        self.ideal_E = None
        '''Ideal energy level for a 'zero' potential, for comparison in a convergence test. Calculated automatically with Data.get_ideal_E()'''


    def to_dict(self):
        return {
            'version': self.version,
            'comment': self.comment,

            'variables': [v.to_dict() for v in self.variables],
            'solutions': [s.to_dict() for s in self.solutions],

            'write_summary': self.write_summary,
            'separate_plots': self.separate_plots,
            'plot_label': self.plot_label,
            'plot_label_position': self.plot_label_position,

            # Convergence tests
            'check_E_level': self.check_E_level,
            'check_E_diff': self.check_E_diff,
            'check_E_threshold': self.check_E_threshold,
            'ideal_E': self.ideal_E,
        }


    # Returns an array of grouped Data objects with the same potential_values and different atom_type
    def group_by_potential(self):
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


    def add(self, *args):
        for value in args:
            if isinstance(value, Data):
                self.variables.extend(value.variables)
                self.solutions.extend(value.solutions)
                if len(self.solutions) == 0:
                    self.version = value.version
                if self.comment is None:
                    self.comment = value.variables[0].comment if value.comment is None else value.comment
                if self.write_summary is None:
                    self.write_summary = value.write_summary
                if self.separate_plots is None:
                    self.separate_plots = value.separate_plots
                if self.plot_label is None:
                    self.plot_label = value.plot_label
                if self.plot_label_position is None:
                    self.plot_label_position = value.plot_label_position
                if self.check_E_level is None:
                    self.check_E_level = value.check_E_level
                if self.check_E_diff is None:
                    self.check_E_diff = value.check_E_diff
                if self.check_E_threshold is None:
                    self.check_E_threshold = value.check_E_threshold
                if self.ideal_E is None:
                    self.ideal_E = value.ideal_E
            elif isinstance(value, Variables):
                self.variables.append(value)
            elif isinstance(value, Solutions):
                self.solutions.append(value)
            else:
                raise TypeError(f'Data.add() can only add Data, Variables and Solutions objects, not {type(value)}.')


    def energies(self):
        energies = []
        for solution in self.solutions:
            if all(solution.eigenvalues):
                energies.append(solution.eigenvalues)
            else:
                energies.append(None)
        return energies


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
    

    def gridsizes(self):
        gridsizes = []
        for variable in self.variables:
            if variable.gridsize:
                gridsizes.append(variable.gridsize)
            else:
                gridsizes.append(None)
        return gridsizes
    

    def runtimes(self):
        runtimes = []
        for solution in self.solutions:
            if solution.runtime:
                runtimes.append(solution.runtime)
            else:
                runtimes.append(None)
        return runtimes


    def atom_types(self):
        atom_types = []
        for variable in self.variables:
            if variable.atom_type not in atom_types:
                atom_types.append(variable.atom_type)
        return atom_types

    
    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.__dict__.update(data)
        obj.variables = [Variables.from_dict(v) for v in data['variables']]
        obj.solutions = [Solutions.from_dict(s) for s in data['solutions']]
        return obj

