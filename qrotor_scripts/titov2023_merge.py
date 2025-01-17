import qrotor as qr
import os
from math import sqrt


filenames = ['out1', 'out2', 'out3', 'out4', 'out5']
# filenames = ['out_op1', 'out_op2', 'out_op3', 'out_op4', 'out_op5']

output = qr.logdirfile + '_titov2023_converged'
# output = qr.logdirfile + '_titov2023_overpowered'

data = qr.Data()

for filename in filenames:
    try:
        file = os.path.join(qr.logdir, filename)
        file_data = qr.file.read(file)
        data.add(file_data)
        print(f'Added  {file}')
    except Exception as e:
        print(f'Skipped  {file}  due to error:  {e}')

data.sort_by_gridsize()

##########  Metadata options  ##########
# data.comment = f'Energies from titov2023. Reproduced with QRotor, gridsize 200000'
# data.write_summary = True
# data.plot_label = True
# data.plot_label_position = [0.5, 0.5, 'center', 'center']
for i, variable in enumerate(data.variables):
    variable.comment = f'Energies from titov2023. Reproduced with QRotor, converged gridsize {variable.gridsize}'
#   variable.comment = f'Energies from titov2023. Reproduced with QRotor, over-powered gridsize {variable.gridsize}'
    variable.comment += f' (#{i+1})'
########################################

qr.file.write(data, output)
qr.file.compress(output)

