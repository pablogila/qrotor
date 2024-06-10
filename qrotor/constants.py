from .common import *
import numpy as np


# Output file
logname = 'out'
logfile = os.path.join(os.getcwd(), logname)
logdirname = 'out'
logdir = os.path.join(os.getcwd(), logdirname)
logdirfile = os.path.join(logdir, logname)
# Create logdir at import if it doesn't exist
if logdirname:
    os.makedirs(logdir, exist_ok=True)

# Conversion factors
eV_to_J = 1.602176634e-19
J_to_eV = 1 / eV_to_J
angstrom_to_m = 1e-10
m_to_angstrom = 1 / angstrom_to_m
amu_to_kg = 1.66053906660e-27
kg_to_amu = 1 / amu_to_kg
eV_to_meV = 1000
meV_to_eV = 0.001

# Physical constants
h = 6.62607015e-34         # J s
h_eVs = h * J_to_eV
hbar = h / (2 * np.pi)  # J s
hbar_eVs = h_eVs / (2 * np.pi)

# Atomic masses
m_H_amu = 1.00784   # H amu (atomic mass units)
m_H = m_H_amu * amu_to_kg
m_D_amu = 2.014102  # D amu
m_D = m_D_amu * amu_to_kg

# Distance between Carbon and Hydrogen atoms
distance_CH = 1.09285   # Angstroms
distance_NH = 1.040263  # Angstroms

# Angles between atoms:  C-C-H  or  N-C-H  etc.
angle_CH_out = 108.7223   # degrees
angle_NH_out = 111.29016  # degrees
angle_CH = 180 - angle_CH_out
angle_NH = 180 - angle_NH_out

# Rotation radius
r_amu = distance_CH * np.sin(np.deg2rad(angle_CH))
r = r_amu * angstrom_to_m

# Inertia, SI units
I_Hydrogen = 3 * (m_H * r**2)
I_Deuterium = 3 * (m_D * r**2)
# Rotational energy. Should be B=0.574 meV for H, according to titov2023
B_Hydrogen = ((hbar**2) / (2 * I_Hydrogen)) * J_to_eV
B_Deuterium = ((hbar**2) / (2 * I_Deuterium)) * J_to_eV

# Potential constants from titov2023 [C1, C2, C3, C4, C5]
constants_zero = [
    [0,0,0,0,0]
    ]

constants_titov2023 = [
    [2.7860, 0.0130,-1.5284,-0.0037,-1.2791],
    [2.6507, 0.0158,-1.4111,-0.0007,-1.2547],
    [2.1852, 0.0164,-1.0017, 0.0003,-1.2061],
    [5.9109, 0.0258,-7.0152,-0.0168, 1.0213],
    [1.4526, 0.0134,-0.3196, 0.0005,-1.1461]
    ]


# Default testing variables object
test_variables = Variables()
test_variables.set_of_constants = constants_titov2023 #constants_titov_1
test_variables.potential_name = 'titov2023'  # 'titov2023' or 'zero'
test_variables.atom_type = 'H'
test_variables.B = B_Hydrogen
test_variables.searched_E_levels = 5
test_variables.gridsize = 100
test_variables.grid = np.linspace(0, 2*np.pi, test_variables.gridsize)
test_variables.write_summary = True

