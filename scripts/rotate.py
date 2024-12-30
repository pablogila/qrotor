import qrotor as qr
import thoth as th

th.call.here()

filename = 'scf.in'
coordinates = [
    'H   0.46260   0.29423   0.75000',
    'H   0.61927   0.34143   0.81972',
    'H   0.61927   0.34143   0.68028'
#    'N   0.55261   0.36773   0.75000',
#    'C   0.49437   0.52899   0.75000',
#    'H   0.42432   0.55012   0.67565',
#    'H   0.59204   0.60292   0.75000',
#    'H   0.42432   0.55012   0.82435'
]
angle = 60
repeat = False

qr.rotate.structure(filename, coordinates, angle, repeat)

