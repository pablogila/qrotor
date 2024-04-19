import qrotor as qr


gridsize_keys = [1000, 2000, 3000, 5000, 10000, 15000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000, 125000, 150000, 175000, 200000, 250000, 300000]

# input_files = qr.logdirfile + '_'
input_files = 'out/QRotor_OUT_'
output = qr.logdirfile + '_convergence'

data = qr.Data()
for gridsize in gridsize_keys:
    try:
        filename = input_files + str(gridsize)
        file_data = qr.file.read(filename)
        data.add(file_data)
    except FileNotFoundError:
        print(f'Skipped missing {filename}.')

qr.file.write(data, output)
qr.file.compress(output)

