<p align="center"><img width="60.0%" src="pics/qrotor.png"></p>
 
QRotor is a Python package used to study molecular rotations,
such as those of methyl and amine groups.
It can calculate their quantum energy levels and wavefunctions,
along with excitations and tunnel splittings.
These quantum systems are represented by the `qrotor.System()` object.

QRotor can obtain custom potentials from DFT,
which are used to solve the quantum system.


---


# Installation

As always, it is recommended to install your packages in a virtual environment:  
```bash
python3 -m venv .venv
source .venv/bin/activate
```


## With pip

Install or upgrade ATON with  
```bash
pip install qrotor -U
```


## From source

Optionally, you can install ATON from the [GitHub repo](https://github.com/pablogila/qrotor/).
Clone the repository or download the [latest stable release](https://github.com/pablogila/qrotor/tags)
as a ZIP, unzip it, and run inside it:  
```bash
pip install .
```


---


# Documentation

QRotor contains the following modules:

| | |
| --- | --- |
| [qrotor.constants](https://pablogila.github.io/qrotor/qrotor/constants.html) | Common bond lengths and inertias |
| [qrotor.system](https://pablogila.github.io/qrotor/qrotor/system.html)       | Definition of the quantum `System` object |
| [qrotor.systems](https://pablogila.github.io/qrotor/qrotor/systems.html)     | Utilities to manage several System objects, such as a list of systems |
| [qrotor.rotate](https://pablogila.github.io/qrotor/qrotor/rotate.html)       | Rotate specific atoms from structural files |
| [qrotor.potential](https://pablogila.github.io/qrotor/qrotor/potential.html) | Potential definitions and loading functions |
| [qrotor.solve](https://pablogila.github.io/qrotor/qrotor/solve.html)         | Solve rotation eigenvalues and eigenvectors |
| [qrotor.plot](https://pablogila.github.io/qrotor/qrotor/plot.html)           | Plotting utilities |

Check the [full documentation online](https://pablogila.github.io/qrotor/).


---


# Usage

## Solving quantum rotational systems

Let's start with a basic calculation of the eigenvalues for a zero potential, corresponding to a free rotor. 
A predefined synthetic potential can be used, see all available options in the [qrotor.potential](https://pablogila.github.io/qrotor/qrotor/potential.html) documentation.
Note that the default energy unit is meV unless stated otherwise.

```python
import qrotor as qr
system = qr.System()
system.gridsize = 200000  # Size of the potential grid
system.B = 1  # Rotational inertia
system.potential_name = 'zero'
system.solve()
print(system.eigenvalues)
# [0.0, 1.0, 1.0, 4.0, 4.0, 9.0, 9.0, ...]  # approx values
```

The accuracy of the calculation increases with bigger gridsizes,
but note that the runtime increases exponentially.

The same calculation can be performed for a methyl group,
in a cosine potential of amplitude 30 meV:

```python
import qrotor as qr
system = qr.System()
system.gridsize = 200000
system.B = qr.B_CH3  # Rotational inertia of a methyl group
system.potential_name = 'cosine'
system.potential_constants = [0, 30, 3, 0]  # Offset, max, freq, phase (for cosine potential)
system.solve()
# Plot potential and eigenvalues
qr.plot.energies(system)
# Plot the first wavefunctions
qr.plot.wavefunction(system, levels=[0,1,2], square=True)
```


## Custom potentials from DFT

QRotor can be used to obtain custom rotational potentials from DFT calculations.
To run a Quantum ESPRESSO SCF calculation for a methyl rotation every 10 degrees:

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
# Compile a 'potential.csv' file with the calculated potential as a function of the angle, and load it into a new system
system = qr.potential.from_qe()
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
print(system.splittings)
print(system.excitations)
print(system.deg)
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


---


# Contributing

If you are interested in opening an issue or a pull request, please feel free to do so on [GitHub](https://github.com/pablogila/qrotor/).  
For major changes, please get in touch first to discuss the details.  


## Code style

Please try to follow some general guidelines:  
- Use a code style consistent with the rest of the project.  
- Include docstrings to document new additions.  
- Include automated tests for new features or modifications, see [automated testing](#automated-testing).  
- Arrange function arguments by order of relevance.  


## Automated testing

If you are modifying the source code, you should run the automated tests of the [`tests/`](https://github.com/pablogila/qrotor/tree/main/tests) folder to check that everything works as intended.
To do so, first install PyTest in your environment,
```bash
pip install pytest
```

And then run PyTest inside the main directory,
```bash
pytest -vv
```


## Compiling the documentation

The documentation can be compiled automatically to `docs/qrotor.html` with [Pdoc](https://pdoc.dev/) and [ATON](https://pablogila.github.io/aton), by running:
```shell
python3 makedocs.py
```

This runs Pdoc, updating links and pictures, and using the custom theme CSS template from the `css/` folder.


---


# Citation

QRotor is currently under development.
Please cite it if you use it in your research,
> Pablo Gila-Herranz, *QRotor*, https://pablogila.github.io/qrotor  


---


# License

Copyright (C) 2025 Pablo Gila-Herranz  
This program is free software: you can redistribute it and/or modify
it under the terms of the **GNU Affero General Public License** as published
by the Free Software Foundation, either version **3** of the License, or
(at your option) any later version.  
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the attached GNU Affero General Public License for more details.  

