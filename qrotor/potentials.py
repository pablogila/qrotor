from .common import *


# Redirect to the desired potential energy function
def solve(variables:Variables):
    if variables.potential_name == 'titov2023':
        return titov2023(variables)
    elif variables.potential_name == 'zero':
        return zero(variables)
    elif variables.potential_name == 'test':
        return test(variables)
    else:
        return custom(variables)


# Potential energy function of the hindered methyl rotor, from titov2023
def titov2023(variables:Variables):
    x = variables.x
    C = variables.potential_constants
    return C[0] + C[1] * np.sin(3*x) + C[2] * np.cos(3*x) + C[3] * np.sin(6*x) + C[4] * np.cos(6*x)


# Zero potential
def zero(variables:Variables):
    x = variables.x
    return 0 * x


def test(variables:Variables):
    x = variables.x
    C = variables.potential_constants
    phase = 0
    return C[0] + C[1] * np.cos(3*x + phase)  # A potential as an array resulting from DFT calculations, etc.


def custom(variables:Variables):
    x = variables.x
    return 0 * x

