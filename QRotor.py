import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from sympy import *
import time


# Potential for the hindered methyl rotor
def potential(angle, C):
    V = C[0] + C[1] * np.sin(3*angle) + C[2] * np.cos(3*angle) + C[3] * np.sin(6*angle) + C[4] * np.cos(6*angle)
    return V


# potential constants from titov2023
C0 = [2.7860, 0.0130, -1.5284, -0.0037, -1.2791]
C1 = [2.6507, 0.0158, -1.4111, -0.0007, -1.2547]
C2 = [2.1852, 0.0164, -1.0017, 0.0003, -1.2061]
C3 = [5.9109, 0.0258, -7.0152, -0.0168, 1.0213]
C4 = [1.4526, 0.0134, -0.3196, 0.0005, -1.1461]
constants = [C0, C1, C2, C3, C4]

'''
# Plot all the potentials
for constant in constants:
    angles = np.linspace(-np.pi, np.pi, 1000)
    potentials = potential(angles, constant)
    plt.plot(angles, potentials)
plt.xlabel('Angle / radians')
plt.ylabel('Potential / meV')
plt.title('Hindered methyl rotor potential')
plt.legend(['0', '1', '2', '3', '4']).set_title('Potentials\ntitov2023')
filename = os.path.join(os.getcwd(), 'methyl_potentials.png')
plt.savefig(filename)
'''

# Inertia: B=1/2I
m = 1.00784
r = 1.0  # THIS VALUE IS A PLACEHOLODER, NEEDS TO BE CHANGED
B = 1.0 / 2 * 3*(m * r**2)
# Grid parameters
L = 2*np.pi  # Periodicity
N = 500  # Number of grid points
dx = L / N  # Grid spacing
x = np.linspace(0, L, N)  # Create grid


# Potential energy vector
V = []
for angle in x:
    V.append(potential(angle, constants[0]))
V = Matrix(V)

V_matrix = Matrix(N, N, lambda i, j: V[i] if i == j else 0)
print('V_matrix done')

#  A =
# -2  1  0  0  1
#  1 -2  1  0  0
#  0  1 -2  1  0
#  0  0  1 -2  1
#  1  0  0  1 -2
A = Matrix(N, N, lambda i, j: 1 if abs(i-j) == 1 else -2 if i == j else 1 if abs(i-j) == N-1 else 0)
print('A done')

C = Matrix(N, N, lambda i, j: 1 if abs(i-j) == 1 else 10 if i == j else 1 if abs(i-j) == N-1 else 0)
print('C done')



time_start = time.time()

C_inverse = C**-1
print('C_inv done')

time_elapsed = time.time() - time_start
print('Time elapsed to compute the inverse matrix of dimension ' + str(N) + ': ' + str(time_elapsed))

E = -12*B/(dx**2) * C_inverse * A + V_matrix
print('E done')

eigenvalues = E.eigenvals()
eigenvalues_list = list(eigenvalues)
eigenvalues_sorted = sorted(eigenvalues_list)
print('Eigenvalues:')
print(eigenvalues_sorted)


print('Data saved to eigenvalues.txt')
eigenvalues_str = '\n'.join(map(str, eigenvalues_sorted))
time_elapsed_str = str(time_elapsed)
out_file = os.path.join(os.getcwd(), 'eigenvalues.txt')
with open(out_file, 'w') as f:
    f.write('Time elapsed to compute the inverse matrix of dimension ' + str(N) + ': ' + time_elapsed_str + '\n')
    f.write('Eigenvalues:\n' + eigenvalues_str)
print('Data saved to output.txt')
