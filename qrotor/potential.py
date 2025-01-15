"""
# Description

This module contains functions to calculate the actual `potential_values` of the system.


# Index

| | |
| --- | --- |
| `load()`        | Load a system with a custom potential from a potential file |
| `from_qe()`     | Creates a potential data file from Quantum ESPRESSO outputs |
| `interpolate()` | Interpolates the current QSys.potential_values to a new QSys.gridsize |
| `solve()`       | Solve the potential values based on the potential name |
| `zero()`        | Zero potential |
| `sine()`        | Sine potential |
| `titov2023()`   | Potential of the hidered methyl rotor, as in titov2023. |

---
"""


from .classes import *
from . import constants
import numpy as np
import os
from scipy.interpolate import CubicSpline
import aton.st.alias as alias
import aton.st.file as file
import aton.interface.qe as qe
import aton.phys as phys


def load(
        filepath,
        system:QSys=None,
        angle:str='deg',
        energy:str='eV',
        ) -> QSys:
    """Read a potential rotational energy dataset.

    The file should contain two columns with `angle` and `potential` values.
    Degrees and eV are assumed as default units unless stated in `angle` and `energy`.
    """
    file_path = file.get(filepath)
    system = QSys() if system is None else system
    with open(file_path, 'r') as f:
        lines = f.readlines()
    positions = []
    potentials = []
    for line in lines:
        if line.startswith('#'):
            continue
        position, potential = line.split()
        positions.append(float(position))
        potentials.append(float(potential))
    # Save angles to numpy arrays
    if angle.lower() in alias.units['deg']:
        positions = np.radians(positions)
    elif angle.lower() in alias.units['rad']:
        positions = np.array(positions)
    else:
        raise ValueError(f"Angle unit '{angle}' not recognized.")
    # Save energies to numpy arrays
    if energy.lower() in alias.units['meV']:
        potentials = np.array(potentials) * 1000
    elif energy.lower() in alias.units['ev']:
        potentials = np.array(potentials)
    else:
        raise ValueError(f"Energy unit '{energy}' not recognized.")
    # Set the system
    system.grid = np.array(positions)
    system.gridsize = len(positions)
    system.potential_values = np.array(potentials)
    return system


def from_qe(
        folder,
        filters:str=None,
        output:str='potential.dat',
        ) -> None:
    """Creates a potential data file from Quantum ESPRESSO outputs.

    The angle in degrees is extracted from the output filenames,
    which must follow `whatever_ANGLE.out`.

    Outputs from SCF calculations must be located in the provided `folder`,
    and can be filtered with `filters`.
    The `output` name is `potential.dat` by default.
    """
    files = file.get_list(folder=folder, filters=filters, abspath=True)
    potential_data = '# Angle / deg, Potential / eV\n'
    for filepath in files:
        filepath = file.get(filepath=filepath, filters='.out', return_anyway=True)
        if not filepath:  # Not an output file, skip it
            continue
        content = qe.read_in[filepath]
        if not content['Success']:  # Ignore unsuccessful calculations
            continue
        energy = content['Energy'] * phys.Ry_to_eV
        filename = os.path.basename(filepath)
        splits = filename.split('_')
        angle = splits[-1]
        potential_data.append(f'{angle}, {energy}\n')
    with open(output, 'w') as f:
        f.write(potential_data)
    return None


def interpolate(system:QSys) -> QSys:
    """Interpolates the current `qrotor.classes.QSys.potential_values` to a new grid of size `qrotor.classes.QSys.gridsize`."""
    V = system.potential_values
    grid = system.grid
    gridsize = system.gridsize
    new_grid = np.linspace(0, 2*np.pi, gridsize)
    cubic_spline = CubicSpline(grid, V)
    new_V = cubic_spline(new_grid)
    system.grid = new_grid
    system.potential_values = new_V
    return system


# Redirect to the desired potential energy function
def solve(system:QSys):
    """Solves `QSys.potential_values`, according to the `QSys.potential_name`."""
    if system.potential_name.lower() == 'titov2023':
        return titov2023(system)
    elif system.potential_name.lower() == 'zero':
        return zero(system)
    elif system.potential_name.lower() == 'sine':
        return sine(system)
    elif system.potential_name.lower() == 'test':
        return test(system)
    elif system.potential_values:  # Re
        return system.potential_values
    else:
        raise ValueError(f'Unrecognised potential_name ({system.potential_name}) and no potential_values found in system!')


def zero(system:QSys):
    """Zero potential."""
    x = system.grid
    return 0 * x


def sine(system:QSys):
    """Sine potential.

    If potential_constants are provided, returns:
    $C_0 + C_1 \cdot \sin(3x + C_2)$.
    """
    x = system.grid
    C = system.potential_constants
    C0 = 0
    C1 = 1
    C2 = 0
    if C:
        if len(C) > 0:
            C0 = C[0]
        if len(C) > 1:
            C1 = C[1]
        if len(C) > 2:
            C2 = C[2]
    return C0 + C1 * np.sin(3*x + C2)


def titov2023(system:QSys):
    """Potential energy function of the hindered methyl rotor, from titov2023."""
    x = system.grid
    C = system.potential_constants
    if C is None:
        C = constants.constants_titov2023[0]
    return C[0] + C[1] * np.sin(3*x) + C[2] * np.cos(3*x) + C[3] * np.sin(6*x) + C[4] * np.cos(6*x)

