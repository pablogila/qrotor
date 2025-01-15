"""
# Description

Common constants and default values used in the QRotor subpackage.

Bond lengths and angles were obtained from MAPbI3,
see [*Cryst. Growth Des.* 2024, 24, 391−404](https://doi.org/10.1021/acs.cgd.3c01112).

---
"""


import numpy as np
import os
import aton


version = 'v3.0.11'   ####################    TODO: remove when integrated to ATON


# Distance between Carbon and Hydrogen atoms (measured from MAPbI3)
distance_CH = 1.09285   # Angstroms
"""Distance of the C-H bond, in Angstroms."""
distance_NH = 1.040263  # Angstroms
"""Distance of the N-H bond, in Angstroms."""

# Angles between atoms:  C-C-H  or  N-C-H  etc (from MAPbI3)
angle_CH_external = 108.7223
"""External angle of the X-C-H bond, in degrees."""
angle_NH_external = 111.29016
"""External angle of the X-N-H bond, in degrees."""
angle_CH = 180 - angle_CH_external
"""Internal angle of the X-C-H bond, in degrees."""
angle_NH = 180 - angle_NH_external
"""Internal angle of the X-N-H bond, in degrees."""

# Rotation radius (calculated from distance and angle)
r_CH = distance_CH * np.sin(np.deg2rad(angle_CH)) * aton.phys.A_to_m
"""Rotation radius of the methyl group, in meters."""
r_NH = distance_NH * np.sin(np.deg2rad(angle_NH)) * aton.phys.A_to_m
"""Rotation radius of the amine group, in meters."""

# Inertia, SI units
I_CH = 3 * (aton.phys.atoms['H'].mass * r_CH**2)
"""Inertia of CH3, in uma·m^2."""
I_CD = 3 * (aton.phys.atoms['H'].isotope[2].mass * r_CH**2)
"""Inertia of CD3, in uma·m^2."""
I_NH = 3 * (aton.phys.atoms['H'].mass * r_NH**2)
"""Inertia of NH3, in uma·m^2."""
I_ND = 3 * (aton.phys.atoms['H'].isotope[2].mass * r_NH**2)
"""Inertia of ND3, in uma·m^2."""

# Rotational energy.
B_CH = ((aton.phys.hbar_eV**2) / (2 * I_CH)) * aton.phys.J_to_eV
"""Rotational energy of CH3, in eV·s/uma·m^2."""
B_CD = ((aton.phys.hbar**2) / (2 * I_CD)) * aton.phys.J_to_eV
"""Rotational energy of CD3, in eV·s/uma·m^2."""
B_NH = ((aton.phys.hbar**2) / (2 * I_NH)) * aton.phys.J_to_eV
"""Rotational energy of NH3, in eV·s/uma·m^2."""
B_ND = ((aton.phys.hbar**2) / (2 * I_ND)) * aton.phys.J_to_eV
"""Rotational energy of ND3, in eV·s/uma·m^2."""

# Potential constants from titov2023 [C1, C2, C3, C4, C5]
constants_titov2023 = [
    [2.7860, 0.0130,-1.5284,-0.0037,-1.2791],
    [2.6507, 0.0158,-1.4111,-0.0007,-1.2547],
    [2.1852, 0.0164,-1.0017, 0.0003,-1.2061],
    [5.9109, 0.0258,-7.0152,-0.0168, 1.0213],
    [1.4526, 0.0134,-0.3196, 0.0005,-1.1461]
    ]
"""Potential constants from titov2023."""
constants_titov2023_zero = [
    [0,0,0,0,0]
    ]
"""Zero potential constants."""
