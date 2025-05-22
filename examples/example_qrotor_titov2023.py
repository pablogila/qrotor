"""
This script is used to reproduce the eigenvalues from:
K. Titov et al., Phys. Rev. Mater. 7, 073402 (2023)
https://link.aps.org/doi/10.1103/PhysRevMaterials.7.073402
"""


import qrotor as qr

system = qr.System()
system.potential_name = 'titov2023'
system.B = 0.573  # Titov uses a custom B value, a more accurate one is qr.B_CH3
system.searched_E = 5
system.gridsize = 200000

system = qr.solve.energies(system)
system.comment = 'Reproduced eigenvalues from titov2023 with ATON.QRotor'

precision = 4
print('Degeneracy:', system.deg)
print('Tunnel splitting energy (meV):', round(system.splittings[0], precision))
print('Eigenvalues (meV):')
for value in system.eigenvalues:
    print(round(value, precision))

qr.plot.energies(system)

