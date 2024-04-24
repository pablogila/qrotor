import qrotor as qr
from math import sqrt

file = qr.logdirfile + '_titov2023_converged'
# file = qr.logdirfile + '_titov2023_overpowered'

data = qr.file.read(file)

##########  Plotting options  ##########
# data.plot_label = True  # Can be a bool, or a str for a label title.
# data.plot_label_position = [0.5, 0.5, 'center', 'center']
########################################

qr.plot.energies(data)

