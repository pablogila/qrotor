from .common import *


def energies(data:Data):

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


##### TO-DO
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

