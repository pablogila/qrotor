'''
# Description
This module contains functions to calculate the actual `potential_values` of the system.

# Index
- `solve()`
- `titov2023()`
- `zero()`
- `sine()`
- `test()`
- `custom()`
- `load()`

---
'''


from .classes import *
from . import constants
import numpy as np
import aton.st.alias as alias


# Redirect to the desired potential energy function
def solve(system:System):
    '''Solves the `potential_values` of the system, according to the potential name.'''
    if system.potential_name == 'titov2023':
        return titov2023(system)
    elif system.potential_name == 'zero':
        return zero(system)
    elif system.potential_name == 'sine':
        return sine(system)
    elif system.potential_name == 'test':
        return test(system)
    else:
        return custom(system)


# Potential energy function of the hindered methyl rotor, from titov2023
def titov2023(system:System):
    'Solves the potential energy function of the hindered methyl rotor, from titov2023.'
    x = system.grid
    C = system.potential_constants
    if C is None:
        C = constants.constants_titov2023[0]
    return C[0] + C[1] * np.sin(3*x) + C[2] * np.cos(3*x) + C[3] * np.sin(6*x) + C[4] * np.cos(6*x)


# Zero potential
def zero(system:System):
    '''Returns a zero potential.'''
    x = system.grid
    return 0 * x


def sine(system:System):
    '''Returns a sine potential.'''
    x = system.grid
    C = system.potential_constants
    return C[0] * np.sin(3*x)


def test(system:System):
    '''Returns a test potential. This is a placeholder for testing purposes.'''
    x = system.grid
    C = system.potential_constants
    phase = 0
    return C[0] + C[1] * np.cos(3*x + phase)  # A potential as an array resulting from DFT calculations, etc.


def custom(system:System):
    """Used to keep the previous `aton.qrotor.classes.System.potential_values` of the system.
    
    For example, when those were obtained from an external file, with `aton.qrotor.potential.load()`.
    """
    if system.potential_values:
        return system.potential_values
    else:
        print('WARNING:  No potential_values found in system')


def load(file, system=None, angle:str='deg', energy:str='ev') -> System:                 #########   TODO: integrarlo bien
    """Read a potential rotational energy dataset.

    The file should contain two columns: `angle` and `energy`,
    with degrees and eV as default units.
    """
    if not os.path.exists(file):
        file = os.path.join(os.getcwd(), file)
    if not os.path.exists(file):
        raise FileNotFoundError(f"The file {file} does not exist.")

    system = System() if system is None else system
    with open(file, 'r') as f:
        lines = f.readlines()
    positions = []
    potentials = []
    for line in lines:
        if line.startswith('#'):
            continue
        position, potential = line.split()
        positions.append(float(position))
        potentials.append(float(potential))

    if angle.lower() in alias.units['deg']:
        positions = np.radians(positions)
    elif angle.lower() in alias.units['rad']:
        positions = np.array(positions)
    else:
        raise ValueError(f"Angle unit '{angle}' not recognized.")

    if energy.lower() in alias.units['meV']:
        potentials = np.array(potentials) * 1000
    elif energy.lower() in alias.units['ev']:
        potentials = np.array(potentials)
    else:
        raise ValueError(f"Energy unit '{energy}' not recognized.")

    system.grid = np.array(positions)
    system.gridsize = len(positions)
    system.potential_values = np.array(potentials)
    return system