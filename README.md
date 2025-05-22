<p align="center"><img width="40.0%" src="pics/qrotor.png"></p>
 
QRotor is a Python package used to study molecular rotations,
such as those of methyl and amine groups.
It can calculate their quantum energy levels and wavefunctions,
along with excitations and tunnel splittings.
These quantum systems are represented by the `qrotor.System()` object.

QRotor can obtain custom potentials from DFT,
which are used to solve the quantum system.

Check the [full documentation online](https://pablogila.github.io/qrotor/).


# Index

| | |
| --- | --- |
| [qrotor.system](https://pablogila.github.io/qrotor/qrotor/system.html)       | Definition of the quantum `System` object |
| [qrotor.systems](https://pablogila.github.io/qrotor/qrotor/systems.html)     | Functions to manage several System objects, such as a list of systems |
| [qrotor.rotate](https://pablogila.github.io/qrotor/qrotor/rotate.html)       | Rotate specific atoms from structural files |
| [qrotor.constants](https://pablogila.github.io/qrotor/qrotor/constants.html) | Common bond lengths and inertias |
| [qrotor.potential](https://pablogila.github.io/qrotor/qrotor/potential.html) | Potential definitions and loading functions |
| [qrotor.solve](https://pablogila.github.io/qrotor/qrotor/solve.html)         | Solve rotation eigenvalues and eigenvectors |
| [qrotor.plot](https://pablogila.github.io/qrotor/qrotor/plot.html)           | Plotting functions |


# Usage

## Solving quantum rotational systems

A basic calculation of the eigenvalues for a zero potential goes as follows.
Note that the default energy unit is meV unless stated otherwise.

```python
import qrotor as qr
system = qr.System()
system.gridsize = 200000  # Size of the potential grid
system.B = 1  # Rotational inertia
system.potential_name = 'zero'
system.solve()
system.eigenvalues
# [0.0, 1.0, 1.0, 4.0, 4.0, 9.0, 9.0, ...]  # approx values
```

The accuracy of the calculation increases with bigger gridsizes,
but note that the runtime increases exponentially.

The same calculation can be performed for a methyl group,
in a cosine potential of amplitude 30 meV:

```python
import qrotor as qr
system = qr.System()
system.gridsize = 200000  # Size of the potential grid
system.B = qr.B_CH3  # Rotational inertia of a methyl group
system.potential_name = 'cosine'
system.potential_constants = [0, 30, 3, 0]  # Offset, max, freq, phase (for cos pot.)
system.solve()
# Plot potential and eigenvalues
qr.plot.energies(system)
# Plot the first wavefunctions
qr.plot.wavefunction(system, levels=[0,1,2], square=True)
```


## Custom potentials from DFT

QRotor can be used to obtain custom rotational potentials from DFT calculations.
Using Quantum ESPRESSO, running an SCF calculation for a methyl rotation every 10 degrees:

```python
import qrotor as qr
from aton import api
# Approx crystal positions of the atoms to rotate
atoms = [
    '1.101   1.204   1.307'
    '2.102   2.205   2.308'
    '3.103   3.206   3.309'
]
# Create the input SCF files, saving the filenames to a list
scf_files = qr.rotate.structure_qe('molecule.in', positions=atoms, angle=10, repeat=True)
# Run the Quantum ESPRESSO calculations
api.slurm.sbatch(files=scf_files)
```

To load the calculated potential to a QRotor System,
```python
# Compile a 'potential.csv' file with the calculated potential as a function of the angle
qr.potential.from_qe()
# Load to the system
system = qr.potential.load()
# Solve the system, interpolating to a bigger gridsize
system.B = qr.B_CH3
system.solve(200000)
qr.plot.energies(system)
```


## Tunnel splittings and excitations

Tunnel splittings, excitations and energy level degeneracy
below the potential maximum are also calculated upon solving the system:

```python
system.solve()
system.splittings
system.excitations
system.deg
```

An integer `System.deg` degeneracy (e.g. 3 for methyls)
indicates that the energy levels have been properly estimated.
However, if the degeneracy is a float instead,
please check the splittings and excitations manually from the system eigenvalues.

To export the energies and the tunnel splittings of several calculations to a CSV file:

```python
calculations = [system1, system2, system3]
qr.systems.save_energies(calculations)
qr.systems.save_splittings(calculations)
```

Excitations are calculated using the mean for each energy level
with respect to the ground state.
Tunnel splittings for each level are calculated as the difference between A and E,
considering the mean of the eigenvalues for each sublevel.
See [R. M. Dimeo, American Journal of Physics 71, 885–893 (2003)](https://doi.org/10.1119/1.1538575)
and [A. J. Horsewill, Progress in Nuclear Magnetic Resonance Spectroscopy 35, 359–389 (1999)](https://doi.org/10.1016/S0079-6565(99)00016-3)
for further reference.

