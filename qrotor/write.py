from .common import *
from . import constants


def solutions_OLD(solutions:Solutions, out_file=None):
    output = solutions.comment + '\n'
    output += f'Potential constants:    {solutions.constants}\n'
    output += f'Max potential [meV]:    {solutions.max_potential:.4f}\n'
    output += f'Min potential [meV]:    {solutions.min_potential:.4f}\n'
    output += f'Corrected offset [meV]: {solutions.corrected_offset_potential:.4f}\n'
    output += f'Eigenvalues [meV]:      '
    for value in solutions.eigenvalues:
        output += f'{value:.4f} '
    output += '\n'
    output += f'Energy barrier [meV]:   {solutions.energy_barrier:.4f}\n'
    output += f'E1-E0 transition [meV]: {solutions.first_transition:.4f}\n'
    if solutions.write_eigenvectors:
        output += f'Eigenvectors [meV]:\n'
        for value in solutions.eigenvectors:
            output += f'{value}\n'
        output += '\n'
    output += '\n'

    print(output)
    if out_file:
        with open(out_file, 'a') as f:
            f.write(output)


def variables_OLD(variables:Variables, out_file=None):
    output = '\n' + variables.comment + '\n'
    output += f'Potential name:         {variables.potential}\n'
    output += f'Atom type:              {variables.atom_type}\n'
    output += f'Inertia B [meV]:        {variables.B:.4f}\n'
    output += f'Grid size N:            {variables.grifsize}\n'
    output += f'Energy levels computed: {variables.searched_E_levels}\n'
    if variables.runtime:
        output += f'Runtime [s]:            {variables.runtime:.2f}\n'
    output += '\n\n'
    output += '------------------------------------\n\n'

    print(output)
    if out_file:
        with open(out_file, 'a') as f:
            f.write(output)
            print(f'Data saved at {out_file}\n')


###########################


def fix_extension(out_file, good_extension, bad_extensions=['.txt', '.json', '.csv', '.dat', '.out']):
    if not out_file:
        return None
    if out_file.endswith(good_extension):
        return out_file
    for bad_extension in bad_extensions:
        if out_file.endswith(bad_extension):
            return out_file[:-len(bad_extension)] + good_extension
    return out_file + good_extension


def data(data:Data, out_file=None):
    data_json(data, out_file)
    data_summary(data, out_file)


# Write a human-readable output file
def data_summary(data:Data, out_file=None):
    summary = ''
    if data.comment:
        summary += data.comment + '\n\n'

    for i, variable in enumerate(data.variables):
        var_summary_dict = variable.summary()
        for key, value in var_summary_dict.items():
            summary += f'{key:<28}  {value}\n'
        summary += '\n'
        
        sol_summary_dict = data.solutions[i].summary()
        for key, value in sol_summary_dict.items():
            summary += f'{key:<28}  {value}\n'

        summary += '\n\n------------------------------------\n\n'

        print(summary)

    if data.variables[0].write_summary and out_file:
        out_file = fix_extension(out_file, '.txt')
        with open(out_file, 'a') as f:
            f.write(summary)
            print(f'Summary saved at {out_file}\n')


def data_json(data:Data, out_file=None):
    if not out_file:
        return
    if not out_file.endswith('.json'):
        out_file += '.json'
    try:
        with open(out_file, 'r') as f:
            data_list = json.load(f)
    except:
        data_list = []
    data_list.append(data.to_dict())
    with open(out_file, 'w') as f:
        json.dump(data_list, f)

