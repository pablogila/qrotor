import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh
import matplotlib.pyplot as plt
import os


class Variables:
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


class Solutions:
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


class Data:
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

