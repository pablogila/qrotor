import qrotor as qr
from math import sqrt


files = qr.file.get_files(qr.logdir, ['json', 'json.gz'])
output = qr.logdirfile + '_convergence'
data = qr.Data()
for file in files:
    try:
        file_data = qr.file.read(file)
        data.add(file_data)
        print(f'Added  {file}')
    except Exception as e:
        print(f'Skipped  {file}  due to error:  {e}')

data.sort_by_gridsize()

##########  Metadata options  ##########
data.comment = f'Convergence test with 16 cores at Hyperion'
data.write_summary = True
# data.plot_label = True
# data.plot_label_position = [0.5, 0.5, 'center', 'center']
# data.check_E_level = 4
# data.get_ideal_E()
# data.check_E_threshold = 0.00005
for variable in data.variables:
    variable.comment = f'Convergence test for a grid of size {variable.gridsize}'
########################################

qr.file.write(data, output)
qr.file.compress(output)

