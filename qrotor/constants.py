"""
# Description

Common constants and default inertia values used in QRotor.

Bond lengths and angles were obtained from MAPbI3, see
[K. Drużbicki *et al*., Crystal Growth & Design 24, 391–404 (2024)](https://doi.org/10.1021/acs.cgd.3c01112).
"""


import numpy as np
import periodictable
import scipy.constants as const


# Quick conversion factors
Ry_to_eV = const.physical_constants['Rydberg constant times hc in eV'][0]
"""Quick conversion factor from Rydberg to eV energy."""
Ry_to_meV = Ry_to_eV * 1000
"""Quick conversion factor from Rydberg to meV energy."""
eV_to_Ry = 1 / Ry_to_eV
"""Quick conversion factor from eV to Rydberg."""
meV_to_Ry = 1 / Ry_to_meV
"""Quick conversion factor from meV to Rydberg."""
cm1_to_meV = (const.h * const.c * 100 / const.e) * 1000
"""Quick conversion factor from cm$^{-1}$ to meV."""
meV_to_cm1 = 1/cm1_to_meV
"""Quick conversion factor from meV to cm$^{-1}$."""
amu_to_kg = const.physical_constants['atomic mass constant'][0]
"""Quick conversion factor from amu to kg."""
kg_to_amu = 1 / amu_to_kg
"""Quick conversion factor from kg to amu."""

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
r_CH = distance_CH * np.sin(np.deg2rad(angle_CH)) * 1e-10
"""Rotation radius of the methyl group, in meters."""
r_NH = distance_NH * np.sin(np.deg2rad(angle_NH)) * 1e-10
"""Rotation radius of the amine group, in meters."""

# Inertias, SI units
I_CH3 = 3 * (periodictable.H.mass * amu_to_kg * r_CH**2)
"""Inertia of CH3, in kg·m^2."""
I_CD3 = 3 * (periodictable.D.mass * amu_to_kg * r_CH**2)
"""Inertia of CD3, in kg·m^2."""
I_NH3 = 3 * (periodictable.H.mass * amu_to_kg * r_NH**2)
"""Inertia of NH3, in kg·m^2."""
I_ND3 = 3 * (periodictable.D.mass * amu_to_kg * r_NH**2)
"""Inertia of ND3, in kg·m^2."""

# Inertias of the co-rotation, SI units
I_CH3NH3 = I_CH3 + I_NH3
"""Inertia of CH3NH3+, in kg·m^2."""
I_CD3NH3 = I_CD3 + I_NH3
"""Inertia of CD3NH3+, in kg·m^2."""
I_CH3ND3 = I_CH3 + I_ND3
"""Inertia of CH3ND3+, in kg·m^2."""
I_CD3ND3 = I_CD3 + I_ND3
"""Inertia of CD3ND3+, in kg·m^2."""

# Inertias of the dis-rotation, SI units
I_CH3NH3_dis = 1 / ((1/I_CH3) + (1/I_NH3))
"""Inertia of the disrotatory torsion of CH3NH3+, in kg·m^2."""
I_CD3NH3_dis = 1 / ((1/I_CD3) + (1/I_NH3))
"""Inertia of the disrotatory torsion of CD3NH3+, in kg·m^2."""
I_CH3ND3_dis = 1 / ((1/I_CH3) + (1/I_ND3))
"""Inertia of the disrotatory torsion of CH3ND3+, in kg·m^2."""
I_CD3ND3_dis = 1 / ((1/I_CD3) + (1/I_ND3))
"""Inertia of the disrotatory torsion of CD3ND3+, in kg·m^2."""

# Inertias, atomic units
I_CH3_amu = I_CH3 / (amu_to_kg * 1e-20)
"""Inertia of CH3, in amu·AA^2."""
I_CD3_amu = I_CD3 / (amu_to_kg * 1e-20)
"""Inertia of CD3, in amu·AA^2."""
I_NH3_amu = I_NH3 / (amu_to_kg * 1e-20)
"""Inertia of NH3, in amu·AA^2."""
I_ND3_amu = I_ND3 / (amu_to_kg * 1e-20)
"""Inertia of ND3, in amu·AA^2."""

# Inertias of the co-rotation, amu units
I_CH3NH3_amu = I_CH3_amu + I_NH3_amu
"""Inertia of CH3NH3+, in amu·AA^2."""
I_CD3NH3_amu = I_CD3_amu + I_NH3_amu
"""Inertia of CD3NH3+, in amu·AA^2."""
I_CH3ND3_amu = I_CH3_amu + I_ND3_amu
"""Inertia of CH3ND3+, in amu·AA^2."""
I_CD3ND3_amu = I_CD3_amu + I_ND3_amu
"""Inertia of CD3ND3+, in amu·AA^2."""

# Inertias of the dis-rotation, amu units
I_CH3NH3_dis_amu = I_CH3NH3_dis / (amu_to_kg * 1e-20)
"""Inertia of the disrotatory torsion of CH3NH3+, in amu·AA^2."""
I_CD3NH3_dis_amu = I_CD3NH3_dis / (amu_to_kg * 1e-20)
"""Inertia of the disrotatory torsion of CD3NH3+, in amu·AA^2."""
I_CH3ND3_dis_amu = I_CH3ND3_dis / (amu_to_kg * 1e-20)
"""Inertia of the disrotatory torsion of CH3ND3+, in amu·AA^2."""
I_CD3ND3_dis_amu = I_CD3ND3_dis / (amu_to_kg * 1e-20)
"""Inertia of the disrotatory torsion of CD3ND3+, in amu·AA^2."""

# Rotational energy
_hbar = const.physical_constants['reduced Planck constant'][0]
B_CH3 = ((_hbar**2) / (2 * I_CH3)) * (1000 / const.eV)
"""Kinetic rotational energy of CH3, in meV·s/kg·m^2."""
B_CD3 = ((_hbar**2) / (2 * I_CD3)) * (1000 / const.eV)
"""Kinetic rotational energy of CD3, in meV·s/kg·m^2."""
B_NH3 = ((_hbar**2) / (2 * I_NH3)) * (1000 / const.eV)
"""Kinetic rotational energy of NH3, in meV·s/kg·m^2."""
B_ND3 = ((_hbar**2) / (2 * I_ND3)) * (1000 / const.eV)
"""Kinetic rotational energy of ND3, in meV·s/kg·m^2."""

B_CH3NH3 = ((_hbar**2) / (2 * I_CH3NH3)) * (1000 / const.eV)
"""Kinetic rotational energy of CH3NH3+, in meV·s/kg·m^2."""
B_CD3NH3 = ((_hbar**2) / (2 * I_CD3NH3)) * (1000 / const.eV)
"""Kinetic rotational energy of CD3NH3+, in meV·s/kg·m^2."""
B_CH3ND3 = ((_hbar**2) / (2 * I_CH3ND3)) * (1000 / const.eV)
"""Kinetic rotational energy of CH3ND3+, in meV·s/kg·m^2."""
B_CD3ND3 = ((_hbar**2) / (2 * I_CD3ND3)) * (1000 / const.eV)
"""Kinetic rotational energy of CD3ND3+, in meV·s/kg·m^2."""

B_CH3NH3_dis = ((_hbar**2) / (2 * I_CH3NH3_dis)) * (1000 / const.eV)
"""Kinetic rotational energy of the disrotatory torsion of CH3NH3+, in meV·s/kg·m^2."""
B_CD3NH3_dis = ((_hbar**2) / (2 * I_CD3NH3_dis)) * (1000 / const.eV)
"""Kinetic rotational energy of the disrotatory torsion of CD3NH3+, in meV·s/kg·m^2."""
B_CH3ND3_dis = ((_hbar**2) / (2 * I_CH3ND3_dis)) * (1000 / const.eV)
"""Kinetic rotational energy of the disrotatory torsion of CH3ND3+, in meV·s/kg·m^2."""
B_CD3ND3_dis = ((_hbar**2) / (2 * I_CD3ND3_dis)) * (1000 / const.eV)
"""Kinetic rotational energy of the disrotatory torsion of CD3ND3+, in meV·s/kg·m^2."""

# Potential constants from titov2023 [C1, C2, C3, C4, C5]
constants_titov2023 = [
    [2.7860, 0.0130,-1.5284,-0.0037,-1.2791],  # ZIF-8
    [2.6507, 0.0158,-1.4111,-0.0007,-1.2547],  # ZIF-8 + Ar-1
    [2.1852, 0.0164,-1.0017, 0.0003,-1.2061],  # ZIF-8 + Ar-{1,2}
    [5.9109, 0.0258,-7.0152,-0.0168, 1.0213],  # ZIF-8 + Ar-{1,2,3}
    [1.4526, 0.0134,-0.3196, 0.0005,-1.1461],  # ZIF-8 + Ar-{1,2,4}
    ]
"""Potential constants from
[K. Titov et al., Phys. Rev. Mater. 7, 073402 (2023)](https://link.aps.org/doi/10.1103/PhysRevMaterials.7.073402)
for the `qrotor.potential.titov2023` potential.
In meV units.
"""

