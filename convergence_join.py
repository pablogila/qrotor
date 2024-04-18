import qrotor as qr
import os


gridsizes = [1000, 2000, 3000]

output = qr.logfile + '_convergence'
data = qr.Data()

for gridsize in gridsizes:
    filename = qr.logfile + '_' + str(gridsize)
    file_data = qr.file.read(filename)
    data.add(file_data)

qr.plot.convergence(data)

qr.file.write(data, output)
qr.file.compress(output)

data_new = qr.file.read(output + '.gz')
qr.plot.convergence(data_new)

