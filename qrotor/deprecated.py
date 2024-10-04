## Deprecated in v2.0.1


def grid_2pi(variables:Variables):
    variables.grid = np.linspace(0, 2*np.pi, variables.gridsize)
    return variables


def energies_OLD(variables:Variables, out_file=None):
    data = Data()

    if variables.set_of_constants is None:
        variables.set_of_constants = [[0]]
        if variables.potential_constants is not None:
            variables.set_of_constants = [variables.potential_constants]

    for constants in variables.set_of_constants:
        variables.potential_constants = constants
        variables = potential(variables)

        solutions = schrodinger(variables)
        # solutions.comment = f'{i+1}'

        stored_variables = deepcopy(variables)

        data.variables.append(stored_variables)
        data.solutions.append(solutions)

        if out_file:
            stored_data = Data()
            stored_data.variables.append(stored_variables)
            stored_data.solutions.append(solutions)
            file.write(stored_data, out_file)

    return data

