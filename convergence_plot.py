import qrotor as qr
import os
from math import sqrt

print_version = False

file = qr.logdirfile + '_convergence'
data = qr.file.read(file)

data.variables[0].check_E_level = 4
data.variables[0].get_ideal_E()
data.variables[0].plot_label = False  # Can be a bool, or a str for a label title.
data.variables[0].plot_label_position = [0.5, 0.5, 'center', 'center']
data.comment = f'Convergence test for energy level {data.variables[0].check_E_level} (n={int(sqrt(data.variables[0].ideal_E))})'

if print_version:
    data.comment += f'  (v{qr.version})'

qr.plot.convergence(data)

