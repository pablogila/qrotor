import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh
import matplotlib.pyplot as plt
import os
import time


def time_formatted(time_seconds):
    time_days = time_seconds // 86400
    time_hours = (time_seconds % 86400) // 3600
    time_minutes = (time_seconds % 3600) // 60
    time_secs = int(time_seconds % 60)
    if time_days > 0:
        time_message = f'{time_days} days, {time_hours} hours, {time_minutes} minutes, {time_secs} seconds'
    elif time_hours > 0:
        time_message = f'{time_hours} hours, {time_minutes} minutes, {time_secs} seconds'
    elif time_minutes > 0:
        time_message = f'{time_minutes} minutes, {time_secs} seconds'
    else:
        time_message = f'{time_secs} seconds'
    return time_message


# Potential energy function
def U(x, C):
    return C[0] + C[1] * np.sin(3*x) + C[2] * np.cos(3*x) + C[3] * np.sin(6*x) + C[4] * np.cos(6*x)


# potential constants from titov2023
C0 = [2.7860, 0.0130, -1.5284, -0.0037, -1.2791]
C1 = [2.6507, 0.0158, -1.4111, -0.0007, -1.2547]
C2 = [2.1852, 0.0164, -1.0017, 0.0003, -1.2061]
C3 = [5.9109, 0.0258, -7.0152, -0.0168, 1.0213]
C4 = [1.4526, 0.0134, -0.3196, 0.0005, -1.1461]
constants = [C0, C1, C2, C3, C4]


# Inertia: B=1/2I
m = 1.00784  # H
r = 0.6  # APROX... NEEDS TO BE CHANGED
B = 1.0 / 2 * 3*(m * r**2)
N = 100
x = np.linspace(0, 2*np.pi, N)
dx = x[1] - x[0]

V = 0  # not sure about this...


start_time = time.time()

C = constants[0]

# Hamiltonian matrix
diagonals = [-2*np.ones(len(x)), np.ones(len(x)-1), np.ones(len(x)-1)]
H = -B * diags(diagonals, [0, -1, 1]) / dx**2 + diags(U(x, C))

print(diagonals)

# Solve for eigenvalues and eigenvectors
energies, _ = eigsh(H, 8, which='SM')

# Energy transitions
entrans1 = [(energies[1] - energies[0]) * 0.655]
entrans2 = [(energies[3] - energies[1]) * 0.655]
Vlist = [V * 0.655]
eigenvalues = list(energies)

# Increase potential and recalculate
while V < 50:
    V += 0.01
    Vlist.append(V * 0.655)
    H = -B * diags(diagonals, [0, -1, 1]) / dx**2 + diags(U(x, C))
    energies, _ = eigsh(H, 8, which='SM')
    transone = (energies[1] - energies[0]) * 0.655
    transtwo = (energies[3] - energies[1]) * 0.655
    entrans1.append(transone)
    entrans2.append(transtwo)
    eigenvalues.extend(energies)

# Create matrices
#entransfer1matrix = np.array([Vlist, entrans1])
#entransfer2matrix = np.array([Vlist, entrans2])
#eigenvaluesmatrix = np.array(eigenvalues).reshape(-1, 8)


time_elapsed = time.time() - start_time


# Plot energy transitions
plt.plot(entrans1)
plt.plot(entrans2)
plt.show()

print(energies)

# Plot potential energy
plt.figure(figsize=(10, 6))
plt.plot(x, U(x, C), label='Potential')
plt.xlabel('Angle / radians')
plt.ylabel('Energy / meV')
plt.title('Hindered methyl rotor potential')

# Plot energy eigenvalues
for i in range(len(energies)):
    plt.axhline(y=energies[i], color='r', linestyle='--')

plt.legend()
plt.show()

# Export matrices
#sio.savemat("entr1.mat", {'entransfer1matrix': entransfer1matrix})
#sio.savemat("entr2.mat", {'entransfer2matrix': entransfer2matrix})
#sio.savemat("eigenvalues.mat", {'eigenvaluesmatrix': eigenvaluesmatrix})



elapsed_message = 'Computation time: ' + time_formatted(time_elapsed)
print(elapsed_message)
script_dir = os.path.dirname(os.path.abspath(__file__))
out_file = os.path.join(script_dir, 'eigenvalues.txt')
with open(out_file, 'w') as f:
    f.write(elapsed_message + '\n')
    f.write('Eigenvalues:\n')
    f.write(str(energies))
print('Data saved to eigenvalues.txt')

