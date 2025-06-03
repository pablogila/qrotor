"""
# Description

This module provides straightforward functions to plot QRotor data.


# Index

| | |
| --- | --- |
| `potential()`        | Potential values as a function of the angle |
| `energies()`         | Calculated eigenvalues |
| `reduced_energies()` | Reduced energies E/B as a function of the reduced potential V/B |
| `wavefunction()`     | Selected wavefunctions or squared wavefunctions of a system |
| `splittings()`       | Tunnel splitting energies of a list of systems |
| `convergence()`      | Energy convergence |

---
"""


from .system import System
from . import systems
from . import constants
import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy
import aton.alias as alias


def potential(
        data,
        title:str=None,
        marker='',
        linestyle='-',
        cm:bool=False,
        ) -> None:
    """Plot the potential values of `data` (System object, or list of systems).

    Title can be customized with `title`.
    If empty, system[0].comment will be used as title if no more comments are present.

    `marker` and `linestyle` can be a Matplotlib string or list of strings.
    Optionally, the Viridis colormap can be used with `cm = True`.
    """
    system = systems.as_list(data)
    title_str = title if title else (system[0].comment if (system[0].comment and (len(system) == 1 or not system[-1].comment)) else 'Rotational potential energy')
    # Marker as a list
    if isinstance(marker, list):
        if len(marker) < len(system):
            marker.extend([''] * (len(system) - len(marker)))
    else:
        marker = [marker] * len(system)
    # Linestyle as a list
    if isinstance(linestyle, list):
        if len(linestyle) < len(system):
            linestyle.extend(['-'] * (len(system) - len(linestyle)))
    else:
        linestyle = [linestyle] * len(system)

    plt.figure()
    plt.title(title_str)
    plt.xlabel('Angle / rad')
    plt.ylabel('Potential energy / meV')
    plt.xticks([-2*np.pi, -3*np.pi/2, -np.pi, -np.pi/2, 0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi], [r'$-2\pi$', r'$-\frac{3\pi}{2}$', r'$-\pi$', r'$-\frac{\pi}{2}$', '0', r'$\frac{\pi}{2}$', r'$\pi$', r'$\frac{3\pi}{2}$', r'$2\pi$'])

    if cm:  # Plot using a colormap
        colors = plt.cm.viridis(np.linspace(0, 1, len(system)+1))  # +1 to avoid the lighter tones
        for i, s in enumerate(system):
            plt.plot(s.grid, s.potential_values, marker=marker[i], linestyle=linestyle[i], label=s.comment, color=colors[i])
    else:  # Regular plot
        for i, s in enumerate(system):
            plt.plot(s.grid, s.potential_values, marker=marker[i], linestyle=linestyle[i], label=s.comment)

    if all(s.comment for s in system) and len(system) != 1:
        plt.legend(fontsize='small')

    plt.show()


def energies(
        data,
        title:str=None,
        ) -> None:
    """Plot the eigenvalues of `data` (System or a list of System objects)."""
    if isinstance(data, System):
        var = [data]
    else:  # Should be a list
        systems.as_list(data)
        var = data

    V_colors = ['C0', 'C1', 'C2', 'C3', 'C4']
    E_colors = ['lightblue', 'sandybrown', 'lightgrey', 'lightcoral', 'plum']
    E_linestyles = ['--', ':', '-.']
    edgecolors = E_colors

    V_linestyle = '-'
    title = title if title else (var[0].comment if var[0].comment else 'Energy eigenvalues')
    ylabel_text = f'Energy / meV'
    xlabel_text = 'Angle / radians'

    plt.figure(figsize=(10, 6))
    plt.xlabel(xlabel_text)
    plt.ylabel(ylabel_text)
    plt.title(title)
    plt.xticks([-2*np.pi, -3*np.pi/2, -np.pi, -np.pi/2, 0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi], [r'$-2\pi$', r'$-\frac{3\pi}{2}$', r'$-\pi$', r'$-\frac{\pi}{2}$', '0', r'$\frac{\pi}{2}$', r'$\pi$', r'$\frac{3\pi}{2}$', r'$2\pi$'])

    unique_potentials = []
    unique_groups = []
    for i, system in enumerate(var):
        V_color = V_colors[i % len(V_colors)]
        E_color = E_colors[i % len(E_colors)]
        E_linestyle = E_linestyles[i % len(E_linestyles)]
        edgecolor = edgecolors[i % len(edgecolors)]

        # Plot potential energy if it is unique
        if not any(np.array_equal(system.potential_values, value) for value in unique_potentials):
            unique_potentials.append(system.potential_values)
            plt.plot(system.grid, system.potential_values, color=V_color, linestyle=V_linestyle)

        # Plot eigenvalues
        if any(system.eigenvalues):
            text_offset = 3 * len(unique_groups)
            if system.group not in unique_groups:
                unique_groups.append(system.group)
            for j, energy in enumerate(system.eigenvalues):
                plt.axhline(y=energy, color=E_color, linestyle=E_linestyle)
                # Textbox positions are a bit weird when plotting more than 2 systems, but whatever...
                plt.text(j%3*1.0 + text_offset, energy, f'$E_{{{j}}}$ = {round(energy,4):.04f}', va='top', bbox=dict(edgecolor=edgecolor, boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
            if len(systems.get_groups(var)) > 1:
                plt.plot([], [], color=E_color, label=f'{system.group} Energies')  # Add to legend

    if len(systems.get_groups(var)) > 1:
        plt.subplots_adjust(right=0.85)
        plt.legend(bbox_to_anchor=(1.1, 0.5), loc='center', fontsize='small')

    plt.show()


def reduced_energies(
        data:list,
        title:str=None,
        values:list=[],
        legend:list=[],
        ) -> None:
    """Plots the reduced energy of the system E/B vs the reduced potential energy V/B.

    Takes a `data` list of System objects as input.
    An optional `title` can be specified.

    Optional maximum reduced potential `values` are plotted
    as vertical lines (floats or ints) or regions
    (lists inside the values list, from min to max).
    A `legend` of the same len as `values` can be included.
    These values are assumed to be divided by B by the user.
    """
    if values and (isinstance(values, float) or isinstance(values, int) or isinstance(values, np.float64)):
        values = [values]
    if values and len(values) <= len(legend):
        plot_legend = True
    else:
        plot_legend = False
        legend = [''] * len(values)
    systems.as_list(data)
    title = title if title else (data[0].comment if data[0].comment else 'Reduced energies')
    number_of_levels = data[0].searched_E
    x = []
    for system in data:
        potential_max_B = system.potential_max / system.B
        x.append(potential_max_B)
    colors = plt.cm.viridis(np.linspace(0, 1, number_of_levels+1))  # +1 to avoid the lighter tones
    for i in range(number_of_levels):
        y = []
        for system in data:
            eigenvalues_B_i = system.eigenvalues[i] / system.B
            y.append(eigenvalues_B_i)
        plt.plot(x, y, marker='', linestyle='-', color=colors[i])
    # Add vertical lines in the specified values
    line_colors = plt.cm.tab10(np.linspace(0, 1, len(values)))
    for i, value in enumerate(values):
        if isinstance(value, list):
            min_value = min(value)
            max_value = max(value)
            plt.axvspan(min_value, max_value, color=line_colors[i], alpha=0.2, linestyle='', label=legend[i])
        else:
            plt.axvline(x=value, color=line_colors[i], linestyle='--', label=legend[i], alpha=0.5)
    plt.xlabel('V$_{B}$ / B')
    plt.ylabel('E / B')
    plt.title(title)
    if plot_legend:
        plt.legend()
    plt.show()


def wavefunction(
        system:System,
        title:str=None,
        square:bool=True,
        levels=[0, 1, 2],
        overlap=False,
        yticks:bool=False,
        ) -> None:
    """Plot the wavefunction of a `system` for the specified `levels`.

    Wavefunctions are squared by default, showing the probabilities;
    To show the actual wavefunctions, set `square = False`.

    `levels` can be a list of indexes, or the number of levels to plot.

    Specific wavefunctions can be overlapped with `overlap` as a list with the target indexes.
    The `overlap` value can also be the max number of wavefunctions to add.
    All found wavefunctions can be added together with `overlap = True`;
    but note that this overlap is limited by the number of System.searched_E,
    that must be specified before solving the system.
    Setting `overlap` will ignore the `levels` argument.

    Set `yticks = True` to plot the wavefunction yticks.
    """
    data = deepcopy(system)
    eigenvectors = data.eigenvectors
    title = title if title else (data.comment if data.comment else 'System wavefunction')
    fig, ax1 = plt.subplots()
    plt.title(title)
    ax1.set_xlabel('Angle / radians')
    ax1.set_ylabel('Potential / meV')
    ax1.set_xticks([-2*np.pi, -3*np.pi/2, -np.pi, -np.pi/2, 0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi], [r'$-2\pi$', r'$-\frac{3\pi}{2}$', r'$-\pi$', r'$-\frac{\pi}{2}$', '0', r'$\frac{\pi}{2}$', r'$\pi$', r'$\frac{3\pi}{2}$', r'$2\pi$'])
    ax1.plot(data.grid, data.potential_values, color='blue', linestyle='-')
    ax2 = ax1.twinx()
    if not yticks:
        ax2.set_yticks([])
    ax2.set_ylabel('Squared wavefunction' if square else 'Wavefunction')
    # Set levels list
    if isinstance(levels, int) or isinstance(levels, float):
        levels = [x for x in range(int(levels))]
    if not isinstance(levels, list):
        raise ValueError('levels must be an int or a list of ints')
    # Set overlap if requested
    if overlap == True and isinstance(overlap, bool):
        eigenvectors = [np.sum(eigenvectors, axis=0)]
        levels = [0]
        show_legend = False
    elif overlap is not False and (isinstance(overlap, int) or isinstance(overlap, float)):
        max_int = int(overlap)
        eigenvectors = [np.sum(eigenvectors[:max_int], axis=0)]
        levels = [0]
        show_legend = False
    elif isinstance(overlap, list):
        eigenvectors = [np.sum([eigenvectors[i] for i in overlap], axis=0)]
        levels = [0]
        show_legend = False
    else:
        show_legend = True
    # Square values if so
    if square:
        eigenvectors = [vec**2 for vec in eigenvectors]
    # Plot the wavefunction
    for i in levels:
        ax2.plot(data.grid, eigenvectors[i], linestyle='--', label=f'{i}')
    if show_legend:
        fig.legend(loc='upper right', bbox_to_anchor=(0.9, 0.88), fontsize='small', title='Index')
    plt.show()


def splittings(
        data:list,
        title:str=None,
        units:str='ueV'
        ) -> None:
    """Plot the tunnel splitting energies of a `data` list of systems.

    The different `System.comment` are shown in the horizontal axis.
    An optional `title` can be specified.
    Default units shown are $\\mu$eV (`'ueV'`).
    Available units are: `'ueV'`, `'meV'`, `'Ry'`, or `'B'` (free rotor units).
    """
    title = title if title != None else 'Tunnel splitting energies'
    calcs = deepcopy(data)
    calcs = systems.as_list(calcs)

    fig, ax = plt.subplots()
    ax.set_ylabel("Energy / meV")

    y = [c.splittings[0] for c in calcs]
    x = [c.comment for c in calcs]
    # What units do we want?
    if units.lower() in alias.units['ueV']:
        y = [j * 1000 for j in y]  # Convert meV to micro eV
        ax.set_ylabel("Energy / $\\mu$eV")
    elif units.lower() in alias.units['Ry']:
        y = [j * constants.meV_to_Ry for j in y]
        ax.set_ylabel("Energy / Ry")
    elif units.upper() == 'B':
        y = [j / c.B for j, c in zip(y, calcs)]
        ax.set_ylabel("Energy / B")
    #else:  # It's okay let's use meV

    ax.bar(range(len(y)), y)
    for i, comment in enumerate(x):
        ax.text(x=i, y=0, s=comment+' ', rotation=45, verticalalignment='top', horizontalalignment='right')
    ax.set_xlabel("")
    ax.set_title(title)
    ax.set_xticks([])
    fig.tight_layout()
    plt.show()


def convergence(data:list) -> None:
    """Plot the energy convergence of a `data` list of Systems as a function of the gridsize."""
    systems.as_list(data)
    gridsizes = [system.gridsize for system in data]
    runtimes = [system.runtime for system in data]
    deviations = []  # List of lists, containing all eigenvalue deviations for every system
    searched_E = data[0].searched_E
    for system in data:
        deviation_list = []
        for i, eigenvalue in enumerate(system.eigenvalues):
            ideal_E = systems.get_ideal_E(i)
            deviation = abs(ideal_E - eigenvalue)
            deviation_list.append(deviation)
        deviation_list = deviation_list[1:]  # Remove ground state
        deviations.append(deviation_list)
    # Plotting
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Grid size')
    ax1.set_ylabel('Error / meV')
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax2 = ax1.twinx()
    ax2.set_ylabel('Runtime / s')
    ax2.set_yscale('log')
    ax2.plot(gridsizes, runtimes, color='tab:grey', label='Runtime', linestyle='--')
    colors = plt.cm.viridis(np.linspace(0, 1, searched_E))  # Should be searched_E-1 but we want to avoid lighter colors
    for i in range(searched_E-1):
        if i % 2 == 0:  # Ignore even numbers, since those levels are degenerated.
            continue
        ax1.plot(gridsizes, [dev[i] for dev in deviations], label=f'$E_{{{int((i+1)/2)}}}$', color=colors[i])
    fig.legend(loc='upper right', bbox_to_anchor=(0.9, 0.88), fontsize='small')
    plt.title(data[0].comment if data[0].comment else 'Energy convergence vs grid size')
    plt.show()

