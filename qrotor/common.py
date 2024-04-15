import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh
import matplotlib.pyplot as plt
import os
import json
import time
from copy import deepcopy


class Variables_OLD:
    def __init__(self):
        self.comment = None
        self.runtime = None
        self.atom_type = None
        self.constants = None
        self.set_of_constants = None
        self.searched_E_levels = None
        self.potential = None
        self.potential_values = None
        self.B = None
        self.N = None
        self.x = None


class Solutions_OLD:
    def __init__(self):
        self.comment = None
        self.potential_values = None
        self.constants = None
        self.max_potential = None
        self.min_potential = None
        self.corrected_offset_potential = None
        self.eigenvalues = None
        self.eigenvectors = None
        self.energy_barrier = None
        self.first_transition = None
        self.write_eigenvectors = None


class Data_OLD:
    def __init__(self):
        self.title = None
        self.comment = None
        self.x = None
        self.set_of_potentials = None
        self.set_of_constants = None  # I want to get rid of this
        self.set_of_energies = None
        self.set_of_energies_H = None
        self.set_of_energies_D = None
        self.set_of_eigenvectors = None
        self.set_of_eigenvectors_H = None
        self.set_of_eigenvectors_D = None


class Convergence:
    def __init__(self):
        self.title = None
        self.gridsizes = None
        self.energies = None
        self.runtimes = None
        self.energy_level = None
        self.ideal = None
        self.difference = None




class Variables:
    def __init__(self):
        self.comment = None
        self.atom_type = None
        self.searched_E_levels = None

        # Convergence test
        self.check_E_level = None
        self.check_E_difference = None # if True...
        self.ideal_E = None

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
    

    def to_dict(self):
        return {
            'comment': self.comment,
            'atom_type': self.atom_type,
            'searched_E_levels': self.searched_E_levels,

            'check_E_level': self.check_E_level,
            'check_E_difference': self.check_E_difference,
            'ideal_E': self.ideal_E,

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
            'eigenvalues': self.eigenvalues,
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
    
    @classmethod
    def from_dict(cls, data):
        obj = cls()
        # obj.variables = [Variables.from_dict(v) if isinstance(v, dict) else v for v in data['variables']]
        obj.variables = [Variables.from_dict(v) for v in data['variables']]
        # obj.solutions = [Solutions.from_dict(s) if isinstance(s, dict) else s for s in data['solutions']]
        obj.solutions = [Solutions.from_dict(s) for s in data['solutions']]
        return obj

