from ase.io import read
from ase.visualize import view
import qrotor as qr
import thotpy as th
import maatpy as mt


th.call.here()


filename = 'scf.in'
coordinates = [
    'H   0.46260   0.29423   0.75000',
    'H   0.61927   0.34143   0.81972',
    'H   0.61927   0.34143   0.68028'
#    'N   0.55261   0.36773   0.75000',
#    'C   0.49437   0.52899   0.75000',
#    'H   0.42432   0.55012   0.67565',
#    'H   0.59204   0.60292   0.75000',
#    'H   0.42432   0.55012   0.82435'
]
angle = 60
repeat = False

scf = qr.rotate.structure(filename, coordinates, angle, repeat, True)

parameters = th.qe.read_in(filename)
#celldm1 = parameters['A'] * mt.A_to_bohr
#th.qe.set_value(celldm1, 'celldm(1)', scf)

molecule = read(filename)
#view(molecule)

rotated_molecule = read('scf_60.in')
#view(rotated_molecule)