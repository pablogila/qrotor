from .common import *


def energies_OLD(data:Data):

    xlabel = 'Angle / radians'
    ylabel = 'Energy / meV'
    title = data.title
    V_color = 'C0'
    V_label = 'Potential'

    default_color = 'red'
    default_edgecolor = 'tomato'
    default_linestyle = '-'
    default_label = 'Energies'

    H_color = 'orange'
    H_edgecolor = 'peachpuff'
    H_linestyle = ':'
    H_label = 'H energies'

    D_color = 'orchid'
    D_edgecolor = 'lavender'
    D_linestyle = 'dashed'
    D_label = 'D energies'

    for i, potential in enumerate(data.set_of_potentials):
        # Plot potential energy
        plt.figure(figsize=(10, 6))
        plt.plot(data.x, potential, color=V_color, label=V_label)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(f'{title} (#' + str(i+1) + ')' )
        plt.xticks([0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi],
                   ['0', r'$\frac{\pi}{2}$', r'$\pi$', r'$\frac{3\pi}{2}$', r'$2\pi$'])
        # Plot default set_of_energies
        if data.set_of_energies:
            for j, energy in enumerate(data.set_of_energies[i]):
                plt.axhline(y=energy, color=default_color, linestyle=default_linestyle)
                plt.text(j%3*0.9, energy, f'E$_{j}$ = {energy:.4f}', va='top', bbox=dict(edgecolor=default_edgecolor, boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
            plt.plot([], [], color=default_color, label=default_label)  # Add to legend
        # Plot HYDROGEN set_of_energies_H
        if data.set_of_energies_H:
            for j, energy in enumerate(data.set_of_energies_H[i]):
                plt.axhline(y=energy, color=H_color, linestyle=H_linestyle)
                plt.text(j%3*0.9, energy, f'E$_{j}$ = {energy:.4f}', va='top', bbox=dict(edgecolor=H_edgecolor, boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
            plt.plot([], [], color=H_color, linestyle=H_linestyle, label=H_label)
        # Plot DEUTERIUM set_of_energies_D
        if data.set_of_energies_D:
            for j, energy in enumerate(data.set_of_energies_D[i]):
                plt.axhline(y=energy, color = D_color, linestyle=D_linestyle)
                plt.text(4+j%3*0.9, energy, f'E$_{j}$ = {energy:.4f}', va='top', bbox=dict(edgecolor=D_edgecolor, boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
            plt.plot([], [], color=D_color, linestyle=D_linestyle, label=D_label)  # Add to legend
        plt.subplots_adjust(right=0.85)
        plt.legend(bbox_to_anchor=(1.1, 0.5), loc='center', fontsize='small')
        plt.show()


def eigenvectors(data:Data, levels=None, squared=False, scaling_factor=1):

    xlabel = 'Angle / radians'
    ylabel = 'Energy / meV'
    title = data.title
    V_color = 'lightblue'
    V_label = 'Potential'

    #energy_color = 'red'
    energy_edgecolor = 'lightgrey'
    energy_linestyle = ':'
    energy_label = 'E'

    eigenvector_linestyle = '--'

    # To square the eigenvectors
    if squared:
        eigenvector_label = 'Eigenvect$^2$ '
        square = 2
    else:
        eigenvector_label = 'Eigenvect '
        square = 1
    
    for i, potential in enumerate(data.set_of_potentials):

        # Transpose the 2D array so that each inner array represents a different eigenvector
        eigenvectors_transposed = np.transpose(data.set_of_eigenvectors[i])

        # Plot potential energy
        plt.figure(figsize=(10, 6))
        plt.plot(data.x, potential, color=V_color, label=V_label)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(f'{title} (#' + str(i+1) + ')' )
        if len(data.set_of_potentials) == 1:
            plt.title(f'{title}')
        plt.xticks([0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi],
                   ['0', r'$\frac{\pi}{2}$', r'$\pi$', r'$\frac{3\pi}{2}$', r'$2\pi$'])
        for j, energy in enumerate(data.set_of_energies[i]):
            if levels is not None and j not in levels:
                continue

            color = 'C' + str(j)

            E_label = energy_label + str(j)
            plt.axhline(y=energy, linestyle=energy_linestyle, color=color, label=E_label)
            plt.text(j%3*0.9, energy, f'E$_{j}$ = {energy:.4f}', va='top', bbox=dict(edgecolor=energy_edgecolor, boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))

            eigenvect_label = eigenvector_label + str(j)
            eigenvector = scaling_factor*eigenvectors_transposed[j]**square
            plt.plot(data.x, eigenvector, linestyle=eigenvector_linestyle, label=eigenvect_label, color=color)

        plt.subplots_adjust(right=0.85)
        plt.legend(bbox_to_anchor=(1.1, 0.5), loc='center', fontsize='small')
        plt.text(1.03, 0.9, f'Eigenvects\nscaled x{scaling_factor}', transform=plt.gca().transAxes)
        plt.show()


def energy_convergence(convergence:Convergence):
    fig, ax1 = plt.subplots(figsize=(10, 6))

    energies_transposed = np.transpose(convergence.energies)
    calculated_energies = energies_transposed[convergence.energy_level][0]
    plotted_energies = calculated_energies

    ylabel_text = 'Energy / meV'
    xlabel_text = 'Grid Size'
    color = 'tab:blue'
    yaxes_color = color
    textstr_position_x = 0.88
    textstr_position_y = 0.15
    textstr_alignment_v = 'bottom'
    textstr_alignment_h = 'right'
    ideal = convergence.ideal

    if convergence.difference is not False:
        plotted_energies = np.abs(plotted_energies - convergence.ideal)
        ylabel_text = 'Energy offset / |meV|'
        ideal = 0
        textstr_position_x = 0.5
        textstr_position_y = 0.85
        textstr_alignment_v = 'top'
        textstr_alignment_h = 'center'
    
    if not convergence.runtimes:
        yaxes_color = 'black'

    ax1.plot(convergence.gridsizes, plotted_energies, marker='o', linestyle='-', color=color)
    ax1.set_xlabel(xlabel_text)
    ax1.set_ylabel(ylabel_text, color=yaxes_color)
    ax1.tick_params(axis='y', labelcolor=yaxes_color)
    ax1.axhline(y=ideal, color='grey', linestyle='--')

    props = dict(boxstyle='round', facecolor='white', edgecolor='lightgrey', alpha=0.5)
    textstr = f'Ideal  E={convergence.ideal:.4f}\n'


    if convergence.runtimes:
        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
        color = 'tab:red'
        ax2.set_ylabel('Runtime / s', color=color)  # we already handled the x-label with ax1
        ax2.plot(convergence.gridsizes, convergence.runtimes, marker='o', linestyle='-', color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        textstr += '\n'.join([f'N={convergence.gridsizes[i]}   E={energy:.4f}   t={convergence.runtimes[i]:.2f}' for i, energy in enumerate(calculated_energies)])

    else:
        textstr += '\n'.join([f'N={convergence.gridsizes[i]}   E={energy:.4f}' for i, energy in enumerate(calculated_energies)])

    fig.text(textstr_position_x, textstr_position_y, textstr, fontsize=10, verticalalignment=textstr_alignment_v, horizontalalignment=textstr_alignment_h, bbox=props)

    plt.title(convergence.title)
    plt.show()




def energies(data:Data):

    xlabel = 'Angle / radians'
    ylabel = 'Energy / meV'
    V_color = 'C0'
    V_label = 'Potential'

    E_color_list = ['red', 'purple', 'grey']  # To extend...

    default_color = 'red'
    default_edgecolor = 'tomato'
    default_linestyle = '-'
    default_label = 'Energies'

    atoms_identified = []

    for i, (variables, solutions) in enumerate(zip(data.variables, data.solutions)):

        if variables.atom_type not in atoms_identified:
            atoms_identified.append(variables.atom_type)
        atom_index = atoms_identified.index(variables.atom_type)

        # Plot potential energy
        plt.figure(figsize=(10, 6))
        plt.plot(variables.x, variables.potential_values, color=V_color, label=V_label)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(f'{variables.comment} (#' + str(i+1) + ')' )
        plt.xticks([0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi],
                   ['0', r'$\frac{\pi}{2}$', r'$\pi$', r'$\frac{3\pi}{2}$', r'$2\pi$'])
        # Plot eigenvalues
        if solutions.eigenvalues is not None:
            for j, energy in enumerate(solutions.eigenvalues):
                plt.axhline(y=energy, color=default_color, linestyle=default_linestyle)
                plt.text(j%3*0.9, energy, f'E$_{j}$ = {energy:.4f}', va='top', bbox=dict(edgecolor=default_edgecolor, boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
            plt.plot([], [], color=default_color, label=default_label)  # Add to legend
        plt.subplots_adjust(right=0.85)
        plt.legend(bbox_to_anchor=(1.1, 0.5), loc='center', fontsize='small')
        plt.show()

