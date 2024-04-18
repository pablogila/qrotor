import qrotor as qr


gridsize_keys = [1000, 2000, 3000]

output = qr.logfile + '_convergence'
data = qr.Data()

txt = ''

for gridsize in gridsize_keys:
    filename = qr.logfile + '_' + str(gridsize)
    file_data = qr.file.read(filename)
    data.add(file_data)

qr.file.write(data, output)
qr.file.compress(output)

