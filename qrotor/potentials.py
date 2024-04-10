from qrotor.core import *


# Redirect to the desired potential energy function
def V(variables:Variables):
    if variables.potential_name == 'titov2023':
        return potential_titov2023(variables)
    elif variables.potential_name == 'zero':
        return potential_zero(variables)
    elif variables.potential_name == 'test':
        return potential_test(variables)
    else:
        return potential_custom(variables)


# Potential energy function of the hindered methyl rotor, from titov2023
def potential_titov2023(variables:Variables):
    x = variables.x
    C = variables.constants
    return C[0] + C[1] * np.sin(3*x) + C[2] * np.cos(3*x) + C[3] * np.sin(6*x) + C[4] * np.cos(6*x)


# Zero potential
def potential_zero(variables:Variables):
    x = variables.x
    return 0 * x


def potential_test(variables:Variables):
    x = variables.x
    C = variables.constants
    phase = 0
    return C[0] + C[1] * np.cos(3*x + phase)  # A potential as an array resulting from DFT calculations, etc.


def potential_custom(variables:Variables):
    x = variables.x
    return 0 * x

