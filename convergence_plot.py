import qrotor as qr
import os
from math import sqrt


file = qr.logdirfile + '_convergence'

data = qr.file.read(file)
data.comment = f'Convergence test for energy level {data.variables[0].check_E_level} (n={int(sqrt(data.variables[0].ideal_E))})  ({qr.version})'
data.variables[0].plot_label_position = [0.5, 0.5, 'center', 'center']

qr.plot.convergence(data)

