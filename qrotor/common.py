import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh
import matplotlib.pyplot as plt
import os
import json
import time
from copy import deepcopy


class Variables:
    def __init__(self):
        self.comment = None
        self.atom_type = None
        self.searched_E_levels = None

        self.gridsize = None
        self.grid = None
        self.B = None

        self.potential_name = None
        self.potential_constants = None
        self.set_of_constants = None
        self.potential_values = None

        self.leave_potential_offset = None
        self.corrected_potential_offset = None

        self.write_summary = None
        self.separate_plots = None

        # Convergence test
        self.check_E_level = None
        self.check_E_difference = None # if True...
        self.ideal_E = None


    def to_dict(self):
        return {
            'comment': self.comment,
            'atom_type': self.atom_type,
            'searched_E_levels': self.searched_E_levels,

            'gridsize': self.gridsize,
            'grid': self.grid.tolist() if isinstance(self.grid, np.ndarray) else self.grid,
            'B': self.B,

            'potential_name': self.potential_name,
            'potential_constants': self.potential_constants.tolist() if isinstance(self.potential_constants, np.ndarray) else self.potential_constants,
            'set_of_constants': self.set_of_constants.tolist() if isinstance(self.set_of_constants, np.ndarray) else self.set_of_constants,
            'potential_values': self.potential_values.tolist() if isinstance(self.potential_values, np.ndarray) else self.potential_values,
            
            'leave_potential_offset': self.leave_potential_offset,
            'corrected_potential_offset': self.corrected_potential_offset,

            'write_summary': self.write_summary,
            'separate_plots': self.separate_plots,

            'check_E_level': self.check_E_level,
            'check_E_difference': self.check_E_difference,
            'ideal_E': self.ideal_E,
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
        # obj.grid = np.array(obj.grid) if isinstance(obj.grid, list) else obj.grid
        obj.grid = np.array(obj.grid)
        # obj.potential_values = np.array(obj.potential_values) if isinstance(obj.potential_values, list) else obj.potential_values
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

            # 'eigenvalues': self.eigenvalues.tolist() if isinstance(self.eigenvalues, np.ndarray) else self.eigenvalues,
            'eigenvalues': self.eigenvalues.tolist() if isinstance(self.eigenvalues, np.ndarray) else self.eigenvalues,
            'eigenvectors': self.eigenvectors.tolist() if isinstance(self.eigenvectors, np.ndarray) else self.eigenvectors,
            'energy_barrier': self.energy_barrier,
            'first_transition': self.first_transition,

            'max_potential': self.max_potential,
            'min_potential': self.min_potential,

            'runtime': self.runtime,
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
        self.comment = None
        self.variables = []
        self.solutions = []


    def to_dict(self):
        return {
            'comment': self.comment,
            'variables': [v.to_dict() for v in self.variables],
            'solutions': [s.to_dict() for s in self.solutions],
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
    

    def group_by_convergence(self):
        return  # TO-DO
    

    def add(self, *args):
        for value in args:
            if isinstance(value, Data):
                if self.comment is None:
                    self.comment = value.comment
                self.variables.extend(value.variables)
                self.solutions.extend(value.solutions)
            if isinstance(value, Variables):
                self.variables.append(value)
            elif isinstance(value, Solutions):
                self.solutions.append(value)
            else:
                raise ValueError('Invalid value type: Data.add() method only accepts Data, Variables or Solutions objects.')


    def energies(self):
        energies = []
        for solution in self.solutions:
            energies.append(solution.eigenvalues)
        return energies


    def atom_types(self):
        atom_types = []
        for variable in self.variables:
            if variable.atom_type not in atom_types:
                atom_types.append(variable.atom_type)
        return atom_types

    
    @classmethod
    def from_dict(cls, data):
        obj = cls()
        # obj.variables = [Variables.from_dict(v) if isinstance(v, dict) else v for v in data['variables']]
        obj.variables = [Variables.from_dict(v) for v in data['variables']]
        # obj.solutions = [Solutions.from_dict(s) if isinstance(s, dict) else s for s in data['solutions']]
        obj.solutions = [Solutions.from_dict(s) for s in data['solutions']]
        return obj

