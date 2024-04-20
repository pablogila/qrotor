import qrotor as qr
from math import sqrt


gridsize_keys = [1000, 2000, 3000, 5000, 10000, 15000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000, 125000, 150000, 175000, 200000, 250000, 300000, 350000, 400000]

set_metadata = False

input_files = qr.logdirfile + '_'
output = qr.logdirfile + '_convergence'
data = qr.Data()
for gridsize in gridsize_keys:
    try:
        filename = input_files + str(gridsize)
        file_data = qr.file.read(filename)
        data.add(file_data)
    except FileNotFoundError:
        print(f'Skipped missing  {filename}')

if set_metadata:  # Set the correct metadata here
    data.variables[0].write_summary = True
    data.variables[0].plot_label = True
    data.variables[0].plot_label_position = [0.5, 0.5, 'center', 'center']
    data.variables[0].check_E_level = 4
    data.variables[0].get_ideal_E()
    data.comment = f'Convergence test with 16 cores at Hyperion'

qr.file.write(data, output)
qr.file.compress(output)

