"""
# Description

This module contains functions to calculate the actual `potential_values` of the system.


# Index

User functions:

| | |
| --- | --- |
| `save()`        | Save the potential from a System to a data file |
| `load()`        | Load a System with a custom potential from a potential data file |
| `from_qe()`     | Creates a potential data file from Quantum ESPRESSO outputs |
| `merge()`       | Add and subtract potentials from systems |
| `scale()`       | Scale potential values by a given factor |

To solve the system, optionally interpolating to a new gridsize, use the `System.solve(gridsize)` method.  
However, if you just want to quickly solve or interpolate the potential, check the `System.solve_potential(gridsize)` method.
This will run several checks before applying the following functions automatically:

| | |
| --- | --- |
| `interpolate()` | Interpolates the current `System.potential_values` to a new `System.gridsize` |
| `solve()`       | Solve the potential values based on the potential name |

A synthetic potential can be created by specifying its name in `System.potential_name`,
along with the corresponding `System.potential_constants` if required.
Available potentials are:

| | |
| --- | --- |
| `zero()`        | Zero potential |
| `sine()`        | Sine potential |
| `cosine()`      | Cosine potential |
| `titov2023()`   | Potential of the hindered methyl rotor, as in titov2023. |

---
"""


from .system import System
from . import constants
from . import systems
import numpy as np
import os
from copy import deepcopy
from scipy.interpolate import CubicSpline
import aton.alias as alias
import aton.file as file
import aton.api.qe as qe
from ._version import __version__


def save(
        system:System,
        comment:str='',
        filepath:str='potential.csv',
        angle:str='deg',
        energy:str='meV',
        ) -> None:
    """Save the rotational potential from a `system` to a CSV file.

    The output `filepath` contains angle and energy columns,
    in degrees and meVs by default.
    The units can be changed with `angle` and `energy`,
    but only change these defaults if you know what you are doing.
    An optional `comment` can be included in the header of the file.
    """
    print('Saving potential data file...')
    # Check if a previous potential.dat file exists, and ask to overwrite it
    previous_potential_file = file.get(filepath, return_anyway=True)
    if previous_potential_file:
        print(f"WARNING: Previous '{filepath}' file will be overwritten, proceed anyway?")
        answer = input("(y/n): ")
        if not answer.lower() in alias.boolean[True]:
            print("Aborted.")
            return None
    # Set header
    potential_data = f'## {comment}\n' if comment else f'## {system.comment}\n' if system.comment else ''
    potential_data += '# Rotational potential dataset\n'
    potential_data += f'# Saved with QRotor {__version__}\n'
    potential_data += '# https://pablogila.github.io/qrotor\n'
    potential_data += '#\n'
    # Check that grid and potential values are the same size
    if len(system.grid) != len(system.potential_values):
        raise ValueError('len(system.grid) != len(system.potential_values)')
    grid = system.grid
    potential_values = system.potential_values
    # Convert angle units
    if angle.lower() in alias.units['rad']:
        potential_data += '# Angle/rad,    '
    else:
        grid = np.degrees(grid)
        potential_data += '# Angle/deg,    '
        if not angle.lower() in alias.units['deg']:
            print(f"WARNING: Unrecognised '{angle}' angle units, using degrees instead")
    # Convert energy units
    if energy.lower() in alias.units['meV']:
        potential_data += 'Potential/meV\n'
    elif energy.lower() in alias.units['eV']:
        potential_values = potential_values * 1e-3
        potential_data += 'Potential/eV\n'
    elif energy.lower() in alias.units['Ry']:
        potential_values = potential_values * constants.meV_to_Ry
        potential_data += 'Potential/Ry\n'
    else:
        print(f"WARNING:  Unrecognised '{energy}' energy units, using meV instead")
        potential_data += 'Potential/meV\n'
    potential_data += '#\n'
    # Save all values
    for angle_value, energy_value in zip(grid, potential_values):
        potential_data += f'{angle_value},    {energy_value}\n'
    with open(filepath, 'w') as f:
        f.write(potential_data)
    print(f'Saved to {filepath}')
    # Warn the user if not in default units
    if angle.lower() not in alias.units['deg']:
        print(f"WARNING: You saved the potential in '{angle}' angle units! Remember that QRotor works in degrees!")
    if energy.lower() not in alias.units['meV']:
        print(f"WARNING: You saved the potential in '{energy}' energy units! Remember that QRotor works in meVs!")


def load(
        filepath:str='potential.csv',
        comment:str=None,
        system:System=None,
        angle:str='deg',
        energy:str='meV',
        ) -> System:
    """Read a rotational potential energy datafile.

    The input file in `filepath` should contain two columns with angle and potential energy values.
    Degrees and meV are assumed as default units unless stated in `angle` and `energy`.
    Units will be converted automatically to radians and meV.

    An optional `comment` can be included in the output System.
    Set to the parent folder name by default.

    A previous System object can be provided through `system` to update its potential values.
    """
    file_path = file.get(filepath)
    system = System() if system is None else system
    with open(file_path, 'r') as f:
        lines = f.readlines()
    # Read the comment
    loaded_comment = ''
    if lines[0].startswith('## '):
        loaded_comment = lines[0][3:].strip()
    # Read data
    positions = []
    potentials = []
    for line in lines:
        if line.startswith('#'):
            continue
        position, potential = line.split()
        positions.append(float(position.strip().strip(',').strip()))
        potentials.append(float(potential.strip()))
    # Save angles to numpy arrays
    if angle.lower() in alias.units['deg']:
        positions = np.radians(positions)
    elif angle.lower() in alias.units['rad']:
        positions = np.array(positions)
    else:
        raise ValueError(f"Angle unit '{angle}' not recognized.")
    # Save energies to numpy arrays
    if energy.lower() in alias.units['eV']:
        potentials = np.array(potentials) * 1000
    elif energy.lower() in alias.units['meV']:
        potentials = np.array(potentials)
    elif energy.lower() in alias.units['Ry']:
        potentials = np.array(potentials) * constants.Ry_to_meV
    else:
        raise ValueError(f"Energy unit '{energy}' not recognized.")
    # Set the system
    system.grid = np.array(positions)
    system.gridsize = len(positions)
    system.potential_values = np.array(potentials)
    # System comment as the loaded comment or the parent folder name
    if comment:
        system.comment = comment
    elif loaded_comment:
        system.comment = loaded_comment
    else:
        system.comment = os.path.basename(os.path.dirname(file_path))
    print(f"Loaded {filepath}")
    return system


def from_qe(
        folder=None,
        filepath:str='potential.csv',
        include:list=['.out'],
        exclude:list=['slurm-'],
        energy:str='meV',
        comment:str=None,
        ) -> System:
    """Compiles a rotational potential CSV file from Quantum ESPRESSO outputs,
    created with `qrotor.rotate.structure_qe()`.
    Returns a `System` object with the new potential values.

    The angle in degrees is extracted from the output filenames,
    which must follow `whatever_ANGLE.out`.

    Outputs from SCF calculations must be located in the provided `folder` (CWD if None).
    Files can be filtered by those containing the specified `include` filters,
    excluding those containing any string from the `exclude` list. 
    The output `filepath` name is `'potential.dat'` by default.

    Energy values are saved to meV by dafault, unless specified in `energy`.
    Only change the energy units if you know what you are doing;
    remember that default energy units in QRotor are meV!
    """
    folder = file.get_dir(folder)
    # Check if a previous potential.dat file exists, and ask to overwrite it
    previous_potential_file = file.get(filepath, return_anyway=True)
    if previous_potential_file:
        print(f"WARNING: Previous '{filepath}' file will be overwritten, proceed anyway?")
        answer = input("(y/n): ")
        if not answer.lower() in alias.boolean[True]:
            print("Aborted.")
            return None
    # Get the files to read
    files = file.get_list(folder=folder, include=include, exclude=exclude, abspath=True)
    folder_name = os.path.basename(folder)
    # Set header
    potential_data = f'## {comment}\n' if comment else f'## {folder_name}\n'
    potential_data += '# Rotational potential dataset\n'
    potential_data += f'# Calculated with QE using QRotor {__version__}\n'
    potential_data += '# https://pablogila.github.io/qrotor\n'
    potential_data += '#\n'
    if energy.lower() in alias.units['eV']:
        potential_data += '# Angle/deg,    Potential/eV\n'
    elif energy.lower() in alias.units['meV']:
        potential_data += '# Angle/deg,    Potential/meV\n'
    elif energy.lower() in alias.units['Ry']:
        potential_data += '# Angle/deg,    Potential/Ry\n'
    else:
        potential_data += '# Angle/deg,    Potential/meV\n'
    potential_data += '#\n'
    potential_data_list = []
    print('Extracting the potential as a function of the angle...')
    print('----------------------------------')
    counter_success = 0
    counter_errors = 0
    for file_path in files:
        filename = os.path.basename(file_path)
        file_path = file.get(filepath=file_path, include='.out', return_anyway=True)
        if not file_path:  # Not an output file, skip it
            continue
        content = qe.read_out(file_path)
        if not content['Success']:  # Ignore unsuccessful calculations
            print(f'x   {filename}')
            counter_errors += 1
            continue
        if energy.lower() in alias.units['eV']:
            energy_value = content['Energy'] * constants.Ry_to_eV
        elif energy.lower() in alias.units['meV']:
            energy_value = content['Energy'] * constants.Ry_to_meV
        elif energy.lower() in alias.units['Ry']:
            energy_value = content['Energy']
        else:
            print(f"WARNING: Energy unit '{energy}' not recognized, using meV instead.")
            energy = 'meV'
            energy_value = content['Energy'] * constants.Ry_to_meV
        splits = filename.split('_')
        angle_value = splits[-1].replace('.out', '')
        angle_value = float(angle_value)
        potential_data_list.append((angle_value, energy_value))
        print(f'OK  {filename}')
        counter_success += 1
    # Sort by angle
    potential_data_list_sorted = sorted(potential_data_list, key=lambda x: x[0])
    # Append the sorted values as a string
    for angle_value, energy_value in potential_data_list_sorted:
        potential_data += f'{angle_value},    {energy_value}\n'
    with open(filepath, 'w') as f:
        f.write(potential_data)
    print('----------------------------------')
    print(f'Succesful calculations (OK): {counter_success}')
    print(f'Faulty calculations     (x): {counter_errors}')
    print('----------------------------------')
    print(f'Saved angles and potential values at {filepath}')
    # Warn the user if not in default units
    if energy.lower() not in alias.units['meV']:
        print(f"WARNING: You saved the potential in '{energy}' units! Remember that QRotor works in meVs!")
    new_system = None
    try:
        new_system = load(filepath=filepath, comment=comment, energy=energy)
    except:
        pass
    return new_system


def merge(
        add=[],
        subtract=[],
        comment:str=None
        ) -> System:
    """Add or subtract potentials from different systems.

    Adds the potential values from the systems in `add`,
    removes the ones from `subtract`.
    All systems will be interpolated to the bigger gridsize if needed.

    A copy of the first System will be returned with the resulting potential values,
    with an optional `comment` if indicated.
    """
    add = systems.as_list(add)
    subtract = systems.as_list(subtract)
    gridsizes = systems.get_gridsizes(add)
    gridsizes.extend(systems.get_gridsizes(subtract))
    max_gridsize = max(gridsizes)
    # All gridsizes should be max_gridsize
    for s in add:
        if s.gridsize != max_gridsize:
            s.gridsize = max_gridsize
            s = interpolate(s)
    for s in subtract:
        if s.gridsize != max_gridsize:
            s.gridsize = max_gridsize
            s = interpolate(s)

    if len(add) == 0:
        if len(subtract) == 0:
            raise ValueError('No systems were provided!')
        result = deepcopy(subtract[0])
        result.potential_values = -result.potential_values
        subtract.pop(0)
    else:
        result = deepcopy(add[0])
        add.pop(0)

    for system in add:
        result.potential_values = np.sum([result.potential_values, system.potential_values], axis=0)
    for system in subtract:
        result.potential_values = np.sum([result.potential_values, -system.potential_values], axis=0)
    if comment != None:
        result.comment = comment
    return result


def scale(
        system:System,
        factor:float,
        comment:str=None
        ) -> System:
    """Returns a copy of `system` with potential values scaled by a `factor`.

    An optional `comment` can be included.
    """
    result = deepcopy(system)
    if factor != 0:
        result.potential_values = system.potential_values * factor
    else:
        result.potential_values = np.zeros(system.gridsize)
    if comment != None:
        result.comment = comment
    return result


def interpolate(system:System) -> System:
    """Interpolates the current `System.potential_values`
    to a new grid of size `System.gridsize`.

    This basic function is called by `qrotor.solve.potential()`,
    which is the recommended way to interpolate potentials.
    """
    print(f"Interpolating potential to a grid of size {system.gridsize}...")
    V = system.potential_values
    grid = system.grid
    gridsize = system.gridsize
    new_grid = np.linspace(0, 2*np.pi, gridsize)
    cubic_spline = CubicSpline(grid, V)
    new_V = cubic_spline(new_grid)
    system.grid = new_grid
    system.potential_values = new_V
    return system


def solve(system:System):
    """Solves `System.potential_values`
    according to the `System.potential_name`,
    returning the new `potential_values`.
    Avaliable potential names are `zero`, `sine` and `titov2023`.

    If `System.potential_name` is not present or not recognised,
    the current `System.potential_values` are used.

    This basic function is called by `qrotor.solve.potential()`,
    which is the recommended way to solve potentials.
    """
    data = deepcopy(system)
    # Is there a potential_name?
    if not data.potential_name:
        if data.potential_values is None or len(data.potential_values) == 0:
            raise ValueError(f'No potential_name and no potential_values found in the system!')
    elif data.potential_name.lower() == 'titov2023':
        data.potential_values = titov2023(data)
    elif data.potential_name.lower() in alias.math['0']:
        data.potential_values = zero(data)
    elif data.potential_name.lower() in alias.math['sin']:
        data.potential_values = sine(data)
    elif data.potential_name.lower() in alias.math['cos']:
        data.potential_values = cosine(data)
    # At least there should be potential_values
    #elif not any(data.potential_values):
    elif data.potential_values is None or len(data.potential_values) == 0:
        raise ValueError("Unrecognised potential_name '{data.potential_name}' and no potential_values found")
    return data.potential_values


def zero(system:System):
    """Zero potential.

    $V(x) = 0$
    """
    x = system.grid
    return 0 * np.array(x)


def sine(system:System):
    """Sine potential.

    $V(x) = C_0 + \\frac{C_1}{2} sin(x C_2 + C_3)$  
    With $C_0$ as the potential offset,
    $C_1$ as the max potential value (without considering the offset),
    $C_2$ as the frequency, and $C_3$ as the phase.
    If no `System.potential_constants` are provided, defaults to $sin(3x)$  
    """
    x = system.grid
    C = system.potential_constants
    C0 = 0
    C1 = 1
    C2 = 3
    C3 = 0
    if C:
        if len(C) > 0:
            C0 = C[0]
        if len(C) > 1:
            C1 = C[1]
        if len(C) > 2:
            C2 = C[2]
        if len(C) > 3:
            C3 = C[3]
    return C0 + (C1 / 2) * np.sin(np.array(x) * C2 + C3)


def cosine(system:System):
    """Cosine potential.

    $V(x) = C_0 + \\frac{C_1}{2} cos(x C_2 + C_3)$  
    With $C_0$ as the potential offset,
    $C_1$ as the max potential value (without considering the offset),
    $C_2$ as the frequency, and $C_3$ as the phase.
    If no `System.potential_constants` are provided, defaults to $cos(3x)$  
    """
    x = system.grid
    C = system.potential_constants
    C0 = 0
    C1 = 1
    C2 = 3
    C3 = 0
    if C:
        if len(C) > 0:
            C0 = C[0]
        if len(C) > 1:
            C1 = C[1]
        if len(C) > 2:
            C2 = C[2]
        if len(C) > 3:
            C3 = C[3]
    return C0 + (C1 / 2) * np.cos(np.array(x) * C2 + C3)


def titov2023(system:System):
    """Potential energy function of the hindered methyl rotor, from
    [K. Titov et al., Phys. Rev. Mater. 7, 073402 (2023)](https://link.aps.org/doi/10.1103/PhysRevMaterials.7.073402).  

    $V(x) = C_0 + C_1 sin(3x) + C_2 cos(3x) + C_3 sin(6x) + C_4 cos(6x)$  
    Default constants are `qrotor.constants.constants_titov2023`[0].  
    """
    x = system.grid
    C = system.potential_constants
    if C is None:
        C = constants.constants_titov2023[0]
    return C[0] + C[1] * np.sin(3*x) + C[2] * np.cos(3*x) + C[3] * np.sin(6*x) + C[4] * np.cos(6*x)

