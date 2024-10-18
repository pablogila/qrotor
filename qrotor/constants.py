'''
Common constants and default values for the QRotor package.
'''


from .classes import *
import numpy as np
import os
import maat as mt
# Get Maat from:
# https://github.com/pablogila/Maat


version = 'v3.0.0-rc2'


# Output file
logname = 'out'
logfile = os.path.join(os.getcwd(), logname)
logdirname = 'out'
logdir = os.path.join(os.getcwd(), logdirname)
logdirfile = os.path.join(logdir, logname)
# Create logdir at import if it doesn't exist
#if logdirname:
#    os.makedirs(logdir, exist_ok=True)

# Atomic masses
m_H = mt.mass_kg['H']
m_D = mt.mass_kg['D']

# Distance between Carbon and Hydrogen atoms (from MAPI)
distance_CH = 1.09285   # Angstroms
distance_NH = 1.040263  # Angstroms
# Exterior angles between atoms:  C-C-H  or  N-C-H  etc (from MAPI)
angle_CH_out = 108.7223   # degrees
angle_NH_out = 111.29016  # degrees
angle_CH = 180 - angle_CH_out
angle_NH = 180 - angle_NH_out
# Rotation radius (calculated from distance and angle)
r = distance_CH * np.sin(np.deg2rad(angle_CH)) * mt.A_to_m

# Inertia, SI units
I_H = 3 * (m_H * r**2)
I_D = 3 * (m_D * r**2)
# Rotational energy. Should be B=0.574 meV for H, according to titov2023
B_H = ((mt.hbar**2) / (2 * I_H)) * mt.J_to_eV
B_D = ((mt.hbar**2) / (2 * I_D)) * mt.J_to_eV

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
test_system = System()
test_system.set_of_constants = constants_titov2023 #constants_titov_1
test_system.potential_name = 'titov2023'  # 'titov2023' or 'zero'
test_system.atom_type = 'H'
test_system.B = B_H
test_system.E_levels = 5
test_system.gridsize = 100
test_system.grid = np.linspace(0, 2*np.pi, test_system.gridsize)

