"""
This script is used to calculate and plot the energy convergence as a function of the grid size.
"""


import qrotor as qr


E_levels_to_calculate = 15  # Note that E levels will be degenerated!
gridsizes = [100, 200, 500, 1000, 5000, 10000, 20000, 50000, 100000, 200000]

system_list = []
for gridsize in gridsizes:
    system = qr.System()
    system.potential_name = 'zero'
    system.B = 1
    system.searched_E = E_levels_to_calculate
    system.gridsize = gridsize
    system.solve()
    system_list.append(system)

# Compress and save the calculation to a file
#system_list = aton.qrotor.systems.reduce_size(system_list)
#aton.st.call.here()
#aton.st.file.save(system_list)

qr.plot.convergence(system_list)

