"""
# Description

The `System` object contains all the information needed for a single QRotor calculation.
This class can be loaded directly as `qrotor.System()`.

---
"""


import numpy as np
from .constants import *
from aton import alias
from ._version import __version__


class System:
    """Quantum system.

    Contains all the data for a single QRotor calculation, with both inputs and outputs.

    Energy units are in meV and angles are in radians, unless stated otherwise.
    """
    def __init__(
            self,
            comment: str = None,
            searched_E: int = 21,
            correct_potential_offset: bool = True,
            save_eigenvectors: bool = True,
            group: str = '',
            B: float = B_CH3,
            gridsize: int = 200000,
            grid = [],
            potential_name: str = '',
            potential_constants: list = None,
            potential_values = [],
            ):
        """A new quantum system can be instantiated as `system = qrotor.System()`.
        This new system will contain the default values listed above.
        """
        ## Technical
        self.version = __version__
        """Version of the package used to generate the data."""
        self.comment: str = comment
        """Custom comment for the dataset."""
        self.searched_E: int = searched_E
        """Number of energy eigenvalues to be searched."""
        self.correct_potential_offset: bool = correct_potential_offset
        """Correct the potential offset as `V - min(V)` or not."""
        self.save_eigenvectors: bool = save_eigenvectors
        """Save or not the eigenvectors. Final file size will be bigger."""
        self.group: str = group
        """Chemical group, methyl or amine: `'CH3'`, `'CD3'`, `'NH3'`, `'ND3'`.

        Can be used to set the value of `B` automatically at startup.
        It can also be configured afterwards with `System.set_group()`.
        This group can be used as metadata to analyse different datasets.
        """
        self.set_group(group)  # Normalise the group name, and set the value of B
        ## Potential
        if not B:
            B = self.B
        self.B: float = B
        """Rotational inertia, as in $B=\\frac{\\hbar^2}{2I}$.

        Defaults to the value for a methyl group.
        """
        self.gridsize: int = gridsize
        """Number of points in the grid."""
        self.grid = grid
        """The grid with the points to be used in the calculation.

        Can be set automatically over $2 \\pi$ with `System.set_grid()`.
        Units must be in radians.
        """
        self.potential_name: str = potential_name
        """Name of the desired potential: `'zero'`, `'titov2023'`, `'test'`...

        If empty or unrecognised, the custom potential values inside `System.potential_values` will be used. 
        """
        self.potential_constants: list = potential_constants
        """List of constants to be used in the calculation of the potential energy, in the `qrotor.potential` module."""
        self.potential_values = potential_values
        """Numpy [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html) with the potential values for each point in the grid.

        Can be calculated with a function available in the `qrotor.potential` module,
        or loaded externally with the `qrotor.potential.load()` function.
        Potential energy units must be in meV.
        """
        # Potential values determined upon solving
        self.potential_offset: float = None
        """`min(V)` before offset correction when `correct_potential_offset = True`"""
        self.potential_min: float = None
        """`min(V)`"""
        self.potential_max: float = None
        """`max(V)`"""
        # Energies determined upon solving
        self.eigenvectors = []
        """Eigenvectors, if `save_eigenvectors` is True. Beware of the file size."""
        self.eigenvalues = []
        """Calculated eigenvalues of the system. In meV."""
        self.E_levels: list = []
        """List of `eigenvalues` grouped by energy levels, found below `potential_max`."""
        self.deg: float = None
        """Estimated degeneracy of the `E_levels` found below `potential_max`."""
        self.excitations: list = []
        """Torsional excitations, as the difference between each energy level with respect to the ground state.

        Considers the means between degenerated eigenvalues for all energy levels below `potential_max`.
        """
        self.splittings: list = []
        """Tunnel splitting energies, for every degenerated energy level.
        
        Calculated for all `E_levels` as the difference between
        the mean of the eigenvalues from A and the mean of the eigenvalues from E,
        see [R. M. Dimeo, American Journal of Physics 71, 885–893 (2003)](https://doi.org/10.1119/1.1538575).
        """
        self.energy_barrier: float = None
        """Activation energy or energy barrier, from the ground torsional state to the top of the potential barrier, `max(V) - min(eigenvalues)`"""
        self.runtime: float = None
        """Time taken to solve the eigenvalues."""

    def solve(self, new_gridsize:int=None):
        """Default user method to solve the quantum system.

        The potential can be interpolated to a `new_gridsize`.

        Same as running `qrotor.solve.energies(System)`
        with an optional new gridsize.
        """
        from .solve import energies
        if new_gridsize:
            self.gridsize = new_gridsize
        return energies(self)

    def solve_potential(self, new_gridsize:int=None):
        """Default user method to quickly solve the potential of the quantum system.

        This method does not solve the energies of the system,
        it just computes the potential and sets `System.potential_max`,
        `System.potential_min` and `System.potential_offset` accordingly.
        To solve the potential AND the energies, check `System.solve()`.

        The potential can be interpolated to a `new_gridsize`.

        Same as running `qrotor.solve.potential(System)`
        with an optional new gridsize.
        """
        from .solve import potential
        if new_gridsize:
            self.gridsize = new_gridsize
        return potential(self)

    def change_phase(self, phase:float, calculate:bool=True):
        """Apply a phase shift to the grid and potential values.

        The `phase` should be a multiple of $\\pi$ (e.g., 3/2 for $3\\pi/2$).
        The resulting grid will be expressed between $-2\\pi$ and $2\\pi$.

        The System is solved immediately after the phase change.
        This last step ensures that all eigenvalues and wavefunctions are correct.
        You can override this step with `calculate = False`,
        but remember to solve the System later!
        """
        if not any(self.potential_values) or not any(self.grid):
            raise ValueError("System.potential_values and System.grid must be set before applying a phase shift.")
        # Normalise the phase between 0 and 2
        if abs(phase) >= 2:
            phase = phase % 2
        while phase < 0:
            phase = phase + 2
        # Shift the grid, between -2pi and 2pi
        self.grid = (self.grid + (phase * np.pi))
        # Apply the phase shift to potential values
        phase_points = int((phase / 2) * self.gridsize)
        self.potential_values = np.roll(self.potential_values, phase_points)
        # Check that the grid is still within -2pi and 2pi, otherwise normalise it for a final time
        while self.grid[0] <= (-2 * np.pi + 0.1):  # With a small tolerance
            self.grid = self.grid + 2 * np.pi
        while self.grid[-1] >= 2.5 * np.pi:  # It was not a problem until reaching 5/2 pi
            self.grid = self.grid -2 * np.pi
        print(f'Potential shifted by {phase}π')
        if calculate:
            self.solve()
        return self

    def set_grid(self, gridsize:int=None):
        """Sets the `System.grid` to the specified `gridsize` from 0 to $2\\pi$.

        If the system had a previous grid and potential values,
        it will interpolate those values to the new gridsize,
        using `qrotor.potential.interpolate()`.
        """
        if gridsize == self.gridsize:
            return self  # Nothing to do here
        if gridsize:
            self.gridsize = gridsize
        # Should we interpolate?
        if any(self.potential_values) and any(self.grid) and self.gridsize:
            from .potential import interpolate
            self = interpolate(self)
        # Should we create the values from zero?
        elif self.gridsize:
                self.grid = np.linspace(0, 2*np.pi, self.gridsize)
        else:
            raise ValueError('gridsize must be provided if there is no System.gridsize')
        return self
    
    def set_group(self, group:str=None, B:float=None):
        """Normalise `System.group` name, and set `System.B` based on it."""
        for name in alias.chemical['CH3']:
            if group.lower() == name:
                self.group = 'CH3'
                if not B:
                    B = B_CH3
                self.B = B
                return self
        for name in alias.chemical['CD3']:
            if group.lower() == name:
                self.group = 'CD3'
                if not B:
                    B = B_CD3
                self.B = B
                return self
        for name in alias.chemical['NH3']:
            if group.lower() == name:
                self.group = 'NH3'
                if not B:
                    B = B_NH3
                self.B = B
                return self
        for name in alias.chemical['ND3']:
            if group.lower() == name:
                self.group = 'ND3'
                if not B:
                    B = B_ND3
                self.B = B
                return self
        self.group = group  # No match was found
        self.B = None
        return self

    def reduce_size(self):
        """Discard data that takes too much space,
        like eigenvectors, potential values and grids."""
        self.eigenvectors = []
        self.potential_values = []
        self.grid = []
        return self

    def summary(self):
        """Returns a dict with a summary of the System data."""
        return {
            'version': self.version,
            'comment': self.comment,
            'searched_E': self.searched_E,
            'correct_potential_offset': self.correct_potential_offset,
            'save_eigenvectors': self.save_eigenvectors,
            'group': self.group,
            'B': self.B,
            'gridsize': self.gridsize,
            'potential_name': self.potential_name,
            'potential_constants': self.potential_constants.tolist() if isinstance(self.potential_constants, np.ndarray) else self.potential_constants,
            'potential_offset': self.potential_offset,
            'potential_min': self.potential_min,
            'potential_max': self.potential_max,
            'eigenvalues': self.eigenvalues.tolist() if isinstance(self.eigenvalues, np.ndarray) else self.eigenvalues,
            'E_levels': self.E_levels,
            'deg': self.deg,
            'excitations': self.excitations,
            'splittings': self.splittings,
            'energy_barrier': self.energy_barrier,
            'runtime': self.runtime,
        }

