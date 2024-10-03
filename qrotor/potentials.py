from .core import *
from . import constants


# Redirect to the desired potential energy function
def solve(variables:Variables):
    if variables.potential_name == 'titov2023':
        return titov2023(variables)
    elif variables.potential_name == 'zero':
        return zero(variables)
    elif variables.potential_name == 'sine':
        return sine(variables)
    elif variables.potential_name == 'test':
        return test(variables)
    else:
        return custom(variables)


# Potential energy function of the hindered methyl rotor, from titov2023
def titov2023(variables:Variables):
    x = variables.grid
    C = variables.potential_constants
    if C is None:
        C = constants.constants_titov2023[0]
    return C[0] + C[1] * np.sin(3*x) + C[2] * np.cos(3*x) + C[3] * np.sin(6*x) + C[4] * np.cos(6*x)


# Zero potential
def zero(variables:Variables):
    x = variables.grid
    return 0 * x


def sine(variables:Variables):
    x = variables.grid
    C = variables.potential_constants
    return C[0] * np.sin(3*x)


def test(variables:Variables):
    x = variables.grid
    C = variables.potential_constants
    phase = 0
    return C[0] + C[1] * np.cos(3*x + phase)  # A potential as an array resulting from DFT calculations, etc.


def custom(variables:Variables):
    if variables.potential_values:
        return variables.potential_values
    else:
        print('WARNING:  No potential_values found in variables')

