import qrotor as qr


gridsize_keys = [1000, 2000, 3000, 5000]

output = qr.logdirfile + '_convergence'
data = qr.Data()

txt = ''

for gridsize in gridsize_keys:
    filename = qr.logdirfile + '_' + str(gridsize)
    file_data = qr.file.read(filename)
    data.add(file_data)

qr.file.write(data, output)
qr.file.compress(output)

