from .common import *


def solutions(solutions:Solutions, out_file=None, print_eigenvectors=False):
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
    if print_eigenvectors:
        output += f'Eigenvectors [meV]:\n'
        for value in solutions.eigenvectors:
            output += f'{value}\n'
        output += '\n'
    output += '\n'

    print(output)
    if out_file:
        with open(out_file, 'a') as f:
            f.write(output)


def variables(variables:Variables, out_file=None):
    output = '\n' + variables.comment + '\n'
    output += f'Potential name:         {variables.potential}\n'
    output += f'Atom type:              {variables.atom_type}\n'
    output += f'Inertia B [meV]:        {variables.B:.4f}\n'
    output += f'Grid size N:            {variables.N}\n'
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

