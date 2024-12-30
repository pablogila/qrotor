'''
# Description
This module contains tools to rotate molecular structures.
Working with Quantum ESPRESSO input files.

# Index
- `structure()`
- `rotate_coords_and_save()`
- `locate_all_coords_in_file()`
- `locate_coords_in_file()`
- `rotate_coords()`
- `update_line_with_coords()`

---
'''


import thoth as th
import numpy as np
import re
from .constants import *
import os
from scipy.spatial.transform import Rotation


def structure(filename:str,
              input_coords:list,
              angle:float,
              repeat:bool=False
              ) -> None:
    '''
    Takes a `filename` with a molecular structure.
    Tree or more atomic coordinates are specified in the `input_coords` list.
    These input coordinates can be approximate.
    It rotates these points from their geometrical center by a specific `angle`.
    Additionally, if `repeat=True`, it repeats the same rotation over the whole circunference.
    Finally, it writes the rotated structure(s) as new structural files.
    '''
    coords, lines = locate_all_coords_in_file(input_coords, filename)
    # Rotate the coordinates
    if not repeat:
        rotate_coords_and_save(filename, coords, lines, angle)
        return None
    for i in range(0, 360, angle):
        print(i)
        rotate_coords_and_save(filename, coords, lines, i)
    return None


def rotate_coords_and_save(filename:str,
                           coords:list,
                           lines:list,
                           angle:float
                           ) -> None:
    '''
    Takes some `coords`, rotates them by a given `angle`,
    and updates the corresponding `lines` in a new structural file updated from `filename`.
    '''
    rotated_coords = rotate_coords(coords, angle)
    updated_lines = []
    for i, line in enumerate(lines):
        updated_line = update_line_with_coords(line, rotated_coords[i])
        updated_lines.append(updated_line)
    fixing_dict = {}
    for i in range(len(lines)):
        fixing_dict[lines[i]] = updated_lines[i]
    base_name = os.path.basename(filename)  # scf.in
    name, ext = os.path.splitext(base_name)  # ('scf', '.in')
    new_name = f"{name}_{angle}{ext}"  # scf_angle.in
    comment = f'This structure was rotated by {angle}º with QRotor {version}'
    th.file.from_template(filename, new_name, comment, fixing_dict)


def locate_all_coords_in_file(coords:list,
                              filename:str
                              ) -> tuple:
    '''
    Runs `locate_coords_in_file()` for a list of several atoms.
    '''
    th.call.here()
    filename = th.file.get(filename)
    all_coords = []  # [[x1,y1,z1], [x2,y2,z2], etc]
    all_lines = []  # [line_1, line_2, etc]
    for coord in coords:
        xyz_approx = th.extract.coords(coord)
        xyz, xyz_str = locate_coords_in_file(xyz_approx, filename)
        if xyz is None:
            raise ValueError(f"The following coordinates were not found:\n{coord}")
        all_coords.append(xyz)
        all_lines.append(xyz_str)
    return all_coords, all_lines


def locate_coords_in_file(coords:list,
                          filename:str
                          ) -> tuple:
    '''
    Takes a given list with approximate `coords` and finds the corresponding string in the `filename`.
    Returns a tuple with the full coords, and the original line from the file.
    Raises an error if none or more than one match of coords is found.
    '''
    pattern = rf''
    for coord in coords:
        pattern += rf'\s*{coord}\d+'
    line_coords = th.find.lines(pattern, filename, 0, 0, False, True)
    if len(line_coords) != 1:  # If it failed, maybe the coordinate was rounded. Trying removing one decimal...
        pattern = rf''
        for i in range(len(coords)):
            coords[i] = str(coords[i])[:-1]  # remove last digit
            pattern += rf'\s*{coords[i]}\d+'
        line_coords = th.find.lines(pattern, filename, 0, 0, False, True)
        if len(line_coords) != 1:  # Try a final time!
            pattern = rf''
            for i in range(len(coords)):
                coords[i] = str(coords[i])[:-1]  # remove last two digits
                pattern += rf'\s*{coords[i]}\d+'
            line_coords = th.find.lines(pattern, filename, 0, 0, False, True)
            if len(line_coords) != 1:
                return None, None
    # Get the coords from the matched line
    line_coords = line_coords[0]
    full_coords = th.extract.coords(line_coords)
    # Remove unintended additional numbers
    filtered_coords = []
    for full_coord in full_coords:
        full_coord_str = str(full_coord)
        for coord in coords:
            coord_str = str(coord)
            if coord_str in full_coord_str:
                filtered_coords.append(full_coord)
    return filtered_coords, line_coords


def rotate_coords(coords:list,
                  angle:float
                  ) -> list:
    '''
    Takes a list of spatial coordinates as
    `coords = [[x1,y1,z1], [x2,y2,z2], [x3,y3,z3]], [etc]`.
    Then rotates said coordinates by a given `angle` (degrees),
    taking the perpendicular axis that passes through the
    geometrical center of the first three points as the axis of rotation.
    Any additional coordinates are rotated with the same rotation matrix.
    Returns a list with the updated positions.
    '''
    coords = np.array(coords)
    if len(coords) < 3:
        raise ValueError("At least three coordinates are required to define the rotation axis.")
    # Define the geometrical center of the first three points
    center = np.mean(coords[:3], axis=0)
    # Ensure the axis passes through the geometrical center
    coords_centered = coords - center
    # Define the perpendicular axis (normal to the plane formed by the first three points)
    v1 = coords_centered[1] - coords_centered[0]
    v2 = coords_centered[2] - coords_centered[0]
    axis = np.cross(v1, v2)
    axis = axis / np.linalg.norm(axis)
    # Create the rotation object using scipy
    rotation = Rotation.from_rotvec(np.radians(angle) * axis)
    # Rotate all coordinates around the geometrical center
    rotated_coords_centered = rotation.apply(coords_centered)
    rotated_coords = rotated_coords_centered + center
    return rotated_coords.tolist()
    

def update_line_with_coords(line:str,
                            coords
                            ) -> str:
    '''
    Takes a point as a list of `coords`, and a `line` string.
    Updates the floats in the string with the new coords.
    '''
    float_pattern = r'[-+]?\d*\.\d+'
    parts = re.split(float_pattern, line)
    floats = re.findall(float_pattern, line)
    if len(floats) < 3:
        raise ValueError("The line does not contain at least three floats!")
    new_line = parts[0] + f"{coords[0]:.15f} " + parts[1] + f"{coords[1]:.15f} " + parts[2] + f"{coords[2]:.15f} " + ''.join(parts[3:])
    return new_line

