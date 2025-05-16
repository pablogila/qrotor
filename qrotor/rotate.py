"""
# Description

This submodule contains tools to rotate molecular structures.
Works with Quantum ESPRESSO input files.


# Index

| | |
| --- | --- |
| `structure_qe()`  | Rotate specific atoms from a Quantum ESPRESSO input file |
| `rotate_coords()` | Rotate a specific list of coordinates |

---
"""


import numpy as np
import os
import shutil
from scipy.spatial.transform import Rotation
from .constants import *
import aton.api as api
import aton.txt.extract as extract
import aton.txt.edit as edit


def structure_qe(
        filepath:str,
        positions:list,
        angle:float,
        repeat:bool=False,
        precision:int=3,
        use_centroid:bool=True,
        show_axis:bool=False,
    ) -> list:
    """Rotates atoms from a Quantum ESPRESSO input file.

    Takes a `filepath` with a molecular structure, and three or more atomic `positions` (list).
    These input positions can be approximate, and are used to identify the target atoms.
    The decimal precision in the search for these positions is controlled by `precision`.

    It rotates the atoms by a specific `angle` in degrees.
    Additionally, if `repeat = True` it repeats the same rotation over the whole circunference.
    Finally, it writes the rotated structure(s) to a new structural file(s).
    Returns a list with the output filename(s).

    By default, the rotation axis is defined by the perpendicular vector
    passing through the geometrical center of the first three points.
    To override this and instead use the vector between the first two atoms
    as the rotation axis, set `use_centroid = False`.

    **WARNING: The `positions` list is order-sensitive**.
    If you rotate more than one chemical group in a structure,
    be sure to follow the same direction for each group (e.g. all clockwise)
    to ensure that all axes of rotation point in the same direction.

    To debug, `show_axis = True` adds two additional helium atoms as the rotation vector.

    The resulting rotational potential can be compiled to a CSV file with `qrotor.potential.from_qe()`.
    """
    print('Rotating Quantum ESPRESSO input structure with QRotor...')
    if len(positions) < 3:
        raise ValueError("At least three positions are required to define the rotation axis.")
    lines = []
    full_positions = []
    for position in positions:
        line = api.qe.get_atom(filepath, position, precision)
        lines.append(line)
        pos = extract.coords(line)
        if len(pos) > 3:  # Keep only the first three coordinates
            pos = pos[:3]
        # Convert to cartesian
        pos_cartesian = api.qe.to_cartesian(filepath, pos)
        full_positions.append(pos_cartesian)
        print(f'Found atom: "{line}"')
    # Set the angles to rotate
    if not repeat:
        angles = [angle]
    else:
        angles = range(0, 360, angle)
    # Rotate and save the structure
    outputs = []
    path = os.path.dirname(filepath)
    basename = os.path.basename(filepath)
    name, ext = os.path.splitext(basename)
    print('Rotating the structure...')
    for angle in angles:
        output_name = name + f'_{angle}' + ext
        output = os.path.join(path, output_name)
        rotated_positions_cartesian = rotate_coords(full_positions, angle, use_centroid, show_axis)
        rotated_positions = []
        for coord in rotated_positions_cartesian:
            pos = api.qe.from_cartesian(filepath, coord)
            rotated_positions.append(pos)
        _save_qe(filepath, output, lines, rotated_positions)
        outputs.append(output)
        print(output)
    return outputs


def rotate_coords(
        positions:list,
        angle:float,
        use_centroid:bool=True,
        show_axis:bool=False,
    ) -> list:
    """Rotates geometrical coordinates.

    Takes a list of atomic `positions` in cartesian coordinates, as
    `[[x1,y1,z1], [x2,y2,z2], [x3,y3,z3], [etc]`.
    Then rotates said coordinates by a given `angle` in degrees.
    Returns a list with the updated positions.

    By default, the rotation vector is defined by the perpendicular
    passing through the geometrical center of the first three points.
    To override this and use the vector between the first two atoms
    as the rotation axis, set `use_centroid = False`.

    **WARNING: The `positions` list is order-sensitive**.
    If you rotate more than one chemical group in a structure,
    be sure to follow the same direction for each group (e.g. all clockwise)
    to ensure that all rotation vectors point in the same direction.

    If `show_axis = True` it returns two additional coordinates at the end of the list,
    with the centroid and the rotation vector. Only works with `use_centroid = True`.

    The rotation uses Rodrigues' rotation formula,
    powered by [`scipy.spatial.transform.Rotation.from_rotvec`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.from_rotvec.html#scipy.spatial.transform.Rotation.from_rotvec).
    """
    if len(positions) < 3:
        raise ValueError("At least three atoms must be rotated.")
    if not isinstance(positions[0], list):
        raise ValueError(f"Atomic positions must have the form: [[x1,y1,z1], [x2,y2,z2], [x3,y3,z3], etc]. Yours were:\n{positions}")
    positions = np.array(positions)
    #print(f'POSITIONS: {positions}')  # DEBUG
    # Define the geometrical center
    center_atoms = positions[:2]
    if use_centroid:
        center_atoms = positions[:3]
    center = np.mean(center_atoms, axis=0)
    # Ensure the axis passes through the geometrical center
    centered_positions = positions - center
    # Define the perpendicular axis (normal to the plane formed by the first three points)
    v1 = centered_positions[0] - centered_positions[1]
    v2 = centered_positions[0] - centered_positions[2]
    axis = v1  # Axis defined by the first two points
    if use_centroid:  # Axis defined by the cross product of the first three points
        axis = np.cross(v2, v1)
    axis_length = np.linalg.norm(axis)
    axis = axis / axis_length
    # Create the rotation object using scipy
    rotation = Rotation.from_rotvec(np.radians(angle) * axis)
    # Rotate all coordinates around the geometrical center
    rotated_centered_positions = rotation.apply(centered_positions)
    rotated_positions = (rotated_centered_positions + center).tolist()
    #print(f'ROTATED_POSITIONS: {rotated_positions}')  # DEBUG
    if show_axis and use_centroid:
        rotated_positions.append(center.tolist())
        rotated_positions.append((center + axis).tolist())
    return rotated_positions


def _save_qe(
        filename,
        output:str,
        lines:list,
        positions:list
    ) -> str:
    """Copies `filename` to `output`, updating the old `lines` with the new `positions`.
    
    The angle will be appended at the end of the input prefix to avoid overlapping calculations.
    """
    shutil.copy(filename, output)
    for i, line in enumerate(lines):
        strings = line.split()
        atom = strings[0]
        new_line = f"  {atom}   {positions[i][0]:.15f}   {positions[i][1]:.15f}   {positions[i][2]:.15f}"
        #print(f'OLD LINE: {line}')  # DEBUG
        #print(f'NEW_LINE: {new_line}')  # DEBUG
        edit.replace_line(output, line, new_line, raise_errors=True)
    if len(lines) + 2 == len(positions):  # In case show_axis=True
        additional_positions = positions[-2:]
        for pos in additional_positions:
            pos.insert(0, 'He')
            api.qe.add_atom(output, pos)
    elif len(lines) != len(positions):
        raise ValueError(f"What?!  len(lines)={len(lines)} and len(positions)={len(positions)}")
    # Add angle to calculation prefix
    output_name = os.path.basename(output)
    splits = output_name.split('_')
    angle_str = splits[-1].replace('.in', '')
    prefix = ''
    content = api.qe.read_in(output)
    if 'prefix' in content.keys():
        prefix = content['prefix']
        prefix = prefix.strip("'")
    prefix = "'" + prefix + angle_str + "'"
    api.qe.set_value(output, 'prefix', prefix)
    return output

