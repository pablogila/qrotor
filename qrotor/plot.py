from .core import *


def energies(data:Data):
    if data.separate_plots:
        for variables, solutions in zip(data.variables, data.solutions):
            new_data = Data()
            new_data.comment = variables.comment
            new_data.variables.append(variables)
            new_data.solutions.append(solutions)
            energy(new_data)
    else:
        # Group data with the same potential_values and different atom_type
        grouped_data = data.group_by_potential()
        for i, new_data in enumerate(grouped_data):
            energy(new_data)


def energy(data:Data):
    V_colors = ['C0'] #...
    E_colors = ['red', 'purple', 'grey']  # To extend...
    E_linestyles = ['--', ':', '-.']
    edgecolors = ['tomato', 'purple', 'grey']

    V_linestyle = '-'

    units = data.variables[0].units
    E_units = 'meV'
    if 'meV' in units or 'mev' in units:
        E_units = 'meV'
    elif 'eV' in units or 'ev' in units:
        E_units = 'eV'

    title = data.comment
    ylabel_text = f'Energy / {E_units}'
    xlabel_text = 'Angle / radians'

    plt.figure(figsize=(10, 6))
    plt.xlabel(xlabel_text)
    plt.ylabel(ylabel_text)

    plt.title(title)
    if not data.comment or (len(data.variables) == 1 and data.variables[0].comment):
        plt.title(f'{data.variables[0].comment}')

    plt.xticks([0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi],
                ['0', r'$\frac{\pi}{2}$', r'$\pi$', r'$\frac{3\pi}{2}$', r'$2\pi$'])

    unique_potentials = []
    unique_atom_types = []
    for i, (variables, solutions) in enumerate(zip(data.variables, data.solutions)):
        V_color = V_colors[i % len(V_colors)]
        E_color = E_colors[i % len(E_colors)]
        E_linestyle = E_linestyles[i % len(E_linestyles)]
        edgecolor = edgecolors[i % len(edgecolors)]

        # Plot potential energy if it is unique
        if not any(np.array_equal(variables.potential_values, element) for element in unique_potentials):
            unique_potentials.append(variables.potential_values)
            plt.plot(variables.grid, variables.potential_values, color=V_color, linestyle=V_linestyle)

        # Plot eigenvalues
        if solutions.eigenvalues is not None:
            text_offset = 3 * len(unique_atom_types)
            if variables.atom_type not in unique_atom_types:
                unique_atom_types.append(variables.atom_type)
            for j, energy in enumerate(solutions.eigenvalues):
                plt.axhline(y=energy, color=E_color, linestyle=E_linestyle)
                plt.text(j%3*0.9 + text_offset, energy, f'$E_{{{j}}}$ = {round(energy,4):.04f}', va='top', bbox=dict(edgecolor=edgecolor, boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
            if len(data.atom_types()) > 1:
                plt.plot([], [], color=E_color, label=f'{variables.atom_type} Energies')  # Add to legend

    if len(data.atom_types()) > 1:
        plt.subplots_adjust(right=0.85)
        plt.legend(bbox_to_anchor=(1.1, 0.5), loc='center', fontsize='small')

    plt.show()


def convergence(data:Data):
    fig, ax1 = plt.subplots(figsize=(10, 6))

    E_color = 'C0'
    runtime_color = 'C3'
    yaxes_color = E_color

    converged_color_line = 'lightgrey'

    units = data.variables[0].units
    E_units = 'meV'
    if 'meV' in units or 'mev' in units:
        E_units = 'meV'
    elif 'eV' in units or 'ev' in units:
        E_units = 'eV'

    title = data.comment
    ylabel_text = f'Energy / {E_units}'
    xlabel_text = 'Grid Size'
    runtime_text = 'Runtime / s'

    plot_label = data.plot_label
    plot_label_position = data.plot_label_position
    check_E_threshold = data.check_E_threshold
    check_E_diff = data.check_E_diff
    check_E_level = data.check_E_level
    ideal_E = data.ideal_E
    if check_E_level is None:
        data.check_E_level = len(data.solutions[0].eigenvalues) - 1
        check_E_level = data.check_E_level
        ideal_E = data.get_ideal_E()


    textbox = dict(boxstyle='round', facecolor='white', edgecolor='lightgrey', alpha=0.5)
    textstr = ''

    textstr_position_x = 0.88
    textstr_position_y = 0.15
    textstr_alignment_h = 'right'
    textstr_alignment_v = 'bottom'

    if plot_label_position and isinstance(plot_label_position, list):
        textstr_position_x = data.plot_label_position[0]
        textstr_position_y = data.plot_label_position[1]
        textstr_alignment_h = data.plot_label_position[2]
        textstr_alignment_v = data.plot_label_position[3]

    energies = data.energies()
    energies_transposed = np.transpose(energies)
    plotted_energies = energies_transposed[check_E_level]
    gridsizes = data.gridsizes()
    runtimes = data.runtimes()

    if check_E_diff:
        plotted_energies = np.abs(plotted_energies - ideal_E)
        ylabel_text = 'Energy offset / |meV|'
        textstr_position_x = 0.5
        textstr_position_y = 0.85
        textstr_alignment_v = 'top'
        textstr_alignment_h = 'center'
    
    if not any(runtimes):
        yaxes_color = 'black'

    ax1.plot(gridsizes, plotted_energies, marker='o', linestyle='-', color=E_color)
    ax1.set_xlabel(xlabel_text)
    ax1.set_ylabel(ylabel_text, color=yaxes_color)
    ax1.tick_params(axis='y', labelcolor=yaxes_color)

    if ideal_E is not None:
        if check_E_diff:
            ax1.axhline(y=0, color='grey', linestyle='--')
        else:
            ax1.axhline(y=ideal_E, color='grey', linestyle='--')
            textstr += f'Ideal  E={ideal_E:.4f}\n'
    
    if check_E_threshold and (ideal_E is not None):
        if check_E_diff:
            abs_energies = energy
        else:
            abs_energies = np.abs(plotted_energies - ideal_E)
        for i, energy in enumerate(abs_energies):
            if energy < check_E_threshold:
                #ax1.plot(gridsizes[i], plotted_energies[i], marker=converged_marker, color=E_converged_color)
                ax1.axvline(x=gridsizes[i], color=converged_color_line, linestyle='--')
                textstr += f'Convergence threshold:  {check_E_threshold}\n'
                lower_limit, _ = ax1.get_ylim()
                ax1.text(gridsizes[i], lower_limit, str(gridsizes[i]), fontsize=10, verticalalignment='bottom', horizontalalignment='center')
                break

    if any(runtimes):
        ax2 = ax1.twinx()  # instantiate a second y-axis that shares the same x-axis
        ax2.set_ylabel(runtime_text, color=runtime_color)  # we already handled the x-label with ax1
        ax2.plot(gridsizes, runtimes, marker='o', linestyle='-', color=runtime_color)
        ax2.tick_params(axis='y', labelcolor=runtime_color)
        for i, energy in enumerate(plotted_energies):
            textstr += f'N={gridsizes[i]}   E={round(energy,4):.04f}   t={round(runtimes[i],2):.02f}'
            if i < len(plotted_energies) - 1:
                textstr += '\n'

    else:
        for i, energy in enumerate(plotted_energies):
            textstr += f'N={gridsizes[i]}   E={round(energy,4):.04f}\n'

    if plot_label is not False:
        if isinstance(plot_label, str):
            textstr = plot_label + '\n' + textstr
        fig.text(textstr_position_x, textstr_position_y, textstr, fontsize=10, verticalalignment=textstr_alignment_v, horizontalalignment=textstr_alignment_h, bbox=textbox)

    plt.title(title)
    plt.show()


def reduced_energies(data):
    '''Plots the reduced energy of the system, E/B, vs the reduced potential energy, V/B'''
    number_of_levels = data.variables[0].searched_E_levels
    x = []
    for solution in data.solutions:
        x.append(solution.max_potential_B)
    for i in range(number_of_levels):
        y = []
        for solution in data.solutions:
            y.append(solution.eigenvalues_B[i])
        plt.plot(x, y, marker='', linestyle='-')
    plt.xlabel('V$_{B}$ / B')
    plt.ylabel('E / B')
    plt.title(data.comment)
    plt.show()









'''
###################################################
############  TO FIX:








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




'''