import qrotor as qr
import os
from math import sqrt

# Load the data
#filename = 'OUTPUT.json'
#file = os.path.join(os.getcwd(), filename)
file = qr.out_file


data = qr.read.data(file)
data.comment = f'Convergence test for energy level {data.variables[0].check_E_level} (n={int(sqrt(data.variables[0].ideal_E))})  ({qr.version})'
data.variables[0].plot_label_position = [0.5, 0.5, 'center', 'center']

qr.plot.convergence(data)

