'''
## Description
This module contains tools to rotate molecular structures.

## Index
- `cli()` Command Line Interface

'''


import thoth as th


def cli(filename:str=None):
    if not filename:
        filename = input('Introduce the filename of the structure:  ')
    th.call.here()
    filename = th.file.get(filename)
    print('Insert manually the approximated X Y Z coordinates, press enter to confirm.')
    coords = []  # [(coords_1, coords_1_line),(coords_2, coords_2_line), etc]
    i = 1
    while True:
        input_str = input(f'Introduce the coords for atom {i}:  ')
        if input_str == '':
            if not coords:
                continue
            else:
                print('Coordinates were added.')
                break
        input_coords = th.extract.coords(input_str)
        coords_full, coords_str = locate_coords_in_file(input_coords, filename)
        if coords_full is None:
            print('No match found, please try again!')
            continue
        coords.append((coords_full, coords_str))
        print('The following coords were located:')
        print(coords_str)
        i += 1


def locate_coords_in_file(coords, filename) -> tuple:
    '''
    Takes a given list with approximate `coords` and finds the corresponding string in the `filename`.
    Returns a tuple with the full coords, and the original line from the file.
    Raises an error if none or more than one match of coords is found.
    '''
    pattern = rf''
    for coord in coords:
        pattern += rf'\s*{coord}\d+'
    line_coords = th.find.lines(pattern, filename, 0, 0, False, True)
    if len(line_coords) > 1:
        return None, None
    if len(line_coords) == 0:
        return None, None
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

