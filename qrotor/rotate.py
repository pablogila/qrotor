"""
# Description

This submodule contains tools to rotate molecular structures.
Working with Quantum ESPRESSO input files.


# Index

| | |
| --- | --- |
| `rotate()`        | Rotate specific atoms from a Quantum ESPRESSO input file |
| `rotate_coords()` | Rotate

---
"""


import numpy as np
import os
import shutil
from scipy.spatial.transform import Rotation
from .constants import *
import aton.interface.qe as qe
import aton.text.extract as extract
import aton.text.edit as edit


def qe(
        filepath:str,
        positions:list,
        angle:float,
        repeat:bool=False,
        show_axis:bool=False
    ) -> list:
    """Rotates atoms from a Quantum ESPRESSO input file.

    Takes a `filepath` with a molecular structure, and three or more atomic `positions` (list).
    These input positions can be approximate, and are used to identify the target atoms.
    It rotates these points by the geometrical center of the first three atoms by a specific `angle`.
    Additionally, if `repeat = True` it repeats the same rotation over the whole circunference.
    Finally, it writes the rotated structure(s) to a new structural file(s).
    Returns a list with the output filename(s).

    To debug, `show_axis = True` adds two additional helium atoms as the rotation vector.
    """
    if len(positions) < 3:
        raise ValueError("At least three positions are required to define the rotation axis.")
    lines = []
    full_positions = []
    for position in positions:
        line = qe.get_atom(filepath, position)
        lines.append(line)
        pos = extract.coords(line)
        if len(pos) > 3:  # Keep only the first three coordinates
            pos = pos[:3]
        # Convert to cartesian
        pos_cartesian = qe.to_cartesian(filepath, pos)
        full_positions.append(pos_cartesian)
        print(pos)
        print(pos_cartesian)
        print('')
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
        rotated_positions_cartesian = rotate_coords(full_positions, angle, show_axis)
        rotated_positions = []
        for coord in rotated_positions_cartesian:
            pos = qe.from_cartesian(filepath, coord)
            rotated_positions.append(pos)
        _save_qe(filepath, output, lines, rotated_positions)
        outputs.append(output)
    return outputs


def rotate_coords(
        positions:list,
        angle:float,
        show_axis:bool=False
    ) -> list:
    """Rotates geometrical coordinates.

    Takes a list of atomic `positions` as
    `[[x1,y1,z1], [x2,y2,z2], [x3,y3,z3]], [etc]`.
    Then rotates said coordinates by a given `angle` (degrees),
    taking the perpendicular axis that passes through the
    geometrical center of the first three points as the axis of rotation.
    Any additional coordinates are rotated with the same rotation matrix.
    Returns a list with the updated positions.

    If `show_axis = True` it returns two additional coordinates at the end of the list,
    with the centroid and the rotation vector.
    """
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
    if show_axis:
        rotated_positions.append(center.tolist())
        rotated_positions.append((center + axis).tolist())
    return rotated_positions


def _save_qe(
        filename,
        output:str,
        lines:list,
        positions:list
    ) -> str:
    """Copies `filename` to `output`, updating the old `lines` with the new `positions`."""
    shutil.copy(filename, output)
    for i, line in enumerate(lines):
        strings = line.split()
        atom = strings[0]
        new_line = f"  {atom}   {positions[i][0]:.15f}   {positions[i][1]:.15f}   {positions[i][2]:.15f}"
        edit.replace_line(output, line, new_line)
    if len(lines) == len(positions):
        return output
    elif len(lines) + 2 != len(positions):
        raise ValueError(f"What?!  len(lines)={len(lines)} and len(positions)={len(positions)}")
    # This is only for the show_axis=True case
    additional_positions = positions[-2:]
    for pos in additional_positions:
        pos.insert(0, 'He')
        qe.add_atom(output, pos)
    return output

