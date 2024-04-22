import qrotor as qr
from math import sqrt

file = qr.logdirfile + '_convergence'
data = qr.file.read(file)

##########  Plotting options  ##########
data.check_E_level = 0
data.get_ideal_E()
data.check_E_threshold = 0.00004
# data.check_E_difference = False
# data.plot_label = True  # Can be a bool, or a str for a label title.
# data.plot_label_position = [0.5, 0.5, 'center', 'center']
# data.comment = f'Convergence test'
data.comment += f', for energy level {data.check_E_level} (n={int(sqrt(data.ideal_E))})'
########################################

qr.plot.convergence(data)

