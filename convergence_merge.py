import qrotor as qr
from math import sqrt


# gridsize_keys = [1000, 2000, 3000, 5000, 10000, 15000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000, 125000, 150000, 175000, 200000, 250000, 300000, 350000]

set_metadata = True

files = qr.file.get_files(qr.logdir, ['json', 'json.gz'])
output = qr.logdirfile + '_convergence'
data = qr.Data()
for file in files:
    try:
        file_data = qr.file.read(file)
        data.add(file_data)
    except Exception as e:
        print(f'Skipped  {file}  due to error:  {e}')

data.sort_by_gridsize()

if set_metadata:  # Set the correct metadata here
    data.comment = f'Convergence test with 16 cores at Hyperion'
    data.write_summary = True
    data.plot_label = True
    data.plot_label_position = [0.5, 0.5, 'center', 'center']
    data.check_E_level = 4
    data.get_ideal_E()
    data.check_E_threshold = 0.00005
    for variable in data.variables:
        variable.comment = f'Convergence test for a grid of size {variable.gridsize}'

qr.file.write(data, output)
qr.file.compress(output)

