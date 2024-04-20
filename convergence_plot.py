import qrotor as qr
from math import sqrt

file = qr.logdirfile + '_convergence'
data = qr.file.read(file)

##########  Plotting options  ##########
# data.variables[0].check_E_level = 4
# data.variables[0].get_ideal_E()
# data.variables[0].check_E_difference = False
# data.variables[0].plot_label = True  # Can be a bool, or a str for a label title.
# data.variables[0].plot_label_position = [0.5, 0.5, 'center', 'center']
# data.comment = f'Convergence test'
# data.comment += f', for energy level {data.variables[0].check_E_level} (n={int(sqrt(data.variables[0].ideal_E))})'
########################################

qr.plot.convergence(data)

