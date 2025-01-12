"""
# Description
This module contains tools to rotate molecular structures.
Working with Quantum ESPRESSO input files.

# Index
- `structure()`
- `rotate_atom()`
- `rotate_atoms()`
- `save_rotation()`

---
"""


import thotpy as th
import numpy as np
import re
from .constants import *
import os
from scipy.spatial.transform import Rotation


def structure(
        filepath:str,
        positions:list,
        angle:float,
        repeat:bool=False,
        show_axis:bool=False
    ) -> list:
    """
    Takes a `filepath` with a molecular structure, and tree or more atomic `positions` (list).
    These input positions can be approximate, and are used to identify the target atoms.
    It rotates these points by the geometrical center of the first three atoms by a specific `angle`.
    Additionally, if `repeat=True` it repeats the same rotation over the whole circunference.
    Finally, it writes the rotated structure(s) to a new structural file.
    Returns a list with the output filenames.
    """
    if len(positions) < 3:
        raise ValueError("At least three positions are required to define the rotation axis.")
    lines = []
    full_positions = []
    for position in positions:
        line = aton.get_atom(filepath, position)
        lines.append(line)
        pos = aton.text.extract.coords(line)
        if len(pos) > 3:  # Keep only the first three coordinates
            pos = pos[:3]
        full_positions.append(pos)
    # Set the angles to rotate
    if not repeat:
        angles = [angle]
    else:
        angles = range(0, 360, angle)
    # Rotate and save the structure
    outputs = []
    basename = os.path.basename(filepath)
    name, ext = os.path.splitext(basename)
    for angle in angles:
        output = os.path.join(name + f'_{angle}' + ext)
        rotated_positions = rotate_atoms(full_positions, angle, show_axis)
        save_rotation(filepath, output, lines, rotated_positions)
        outputs.append(output)
    return outputs


def rotate_atoms(
    positions:list,
    angle:float,
    show_axis:bool=False
    ) -> list:
    '''
    Takes a list of atomic `positions` as
    `[[x1,y1,z1], [x2,y2,z2], [x3,y3,z3]], [etc]`.
    Then rotates said coordinates by a given `angle` (degrees),
    taking the perpendicular axis that passes through the
    geometrical center of the first three points as the axis of rotation.
    Any additional coordinates are rotated with the same rotation matrix.
    Returns a list with the updated positions.\n
    If `show_axis=True` it returns two additional coordinates at the end of the list,
    with the centroid and the rotation vector.
    '''
    if len(positions) < 3:
        raise ValueError("At least three coordinates are required to define the rotation axis.")
    positions = np.array(positions)
    # Define the geometrical center of the first three points
    center = np.mean(positions[:3], axis=0)
    # Ensure the axis passes through the geometrical center
    centered_positions = positions - center
    # Define the perpendicular axis (normal to the plane formed by the first three points)
    v1 = centered_positions[0] - centered_positions[1]
    v2 = centered_positions[0] - centered_positions[2]
    axis = np.cross(v2, v1)
    axis_length = np.linalg.norm(axis)
    axis = axis / axis_length
    # Create the rotation object using scipy
    rotation = Rotation.from_rotvec(np.radians(angle) * axis)
    # Rotate all coordinates around the geometrical center
    rotated_centered_positions = rotation.apply(centered_positions)
    rotated_positions = (rotated_centered_positions + center).tolist()
    # Verify that the distance to the axis remains the same for the first three points
    print("\nOriginal, Rotated centered positions:")
    for i in range(3):
        print(centered_positions[i], rotated_centered_positions[i])
    print("\nOriginal, Rotated distances to the rotation axis:")
    for i in range(3):
        original_distance = np.linalg.norm(centered_positions[i])
        rotated_distance = np.linalg.norm(rotated_centered_positions[i])
        print(f"{original_distance}, {rotated_distance}")
    print('')
    if show_axis:
        rotated_positions.append(center.tolist())
        rotated_positions.append((center + axis).tolist())
    return rotated_positions


def save_rotation(
        filename,
        output:str,
        lines:list,
        positions:list
    ) -> str:
    '''
    Takes an input `filename` and updates the `lines` with the new `positions`,
    then saves it as a new `output`.
    '''
    th.file.copy(filename, output)
    for i, line in enumerate(lines):
        strings = line.split()
        atom = strings[0]
        new_line = f"  {atom}   {positions[i][0]:.15f}   {positions[i][1]:.15f}   {positions[i][2]:.15f}"
        th.text.replace_line(output, line, new_line)
    if len(lines) == len(positions):
        return output
    elif len(lines) + 2 != len(positions):
        raise ValueError(f"What?!  len(lines)={len(lines)} and len(positions)={len(positions)}")
    # This is only for the show_axis=True case
    additional_positions = positions[-2:]
    for pos in additional_positions:
        pos.insert(0, 'He')
        th.qe.add_atom(output, pos)
    return output

