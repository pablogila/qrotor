import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh
import matplotlib.pyplot as plt
import os
import time
from sympy import *


# Potential energy function
def V(x, C):
    return C[0] + C[1] * np.sin(3*x) + C[2] * np.cos(3*x) + C[3] * np.sin(6*x) + C[4] * np.cos(6*x)


# potential constants from titov2023
constants_1 = [
    [2.7860, 0.0130,-1.5284,-0.0037,-1.2791],
    [2.6507, 0.0158,-1.4111,-0.0007,-1.2547],
    [2.1852, 0.0164,-1.0017, 0.0003,-1.2061],
    [5.9109, 0.0258,-7.0152,-0.0168, 1.0213],
    [1.4526, 0.0134,-0.3196, 0.0005,-1.1461]
    ]
constants_2 = [
    [2.7860, 0.0130,-1.5284,-0.0037,-1.2791],
    [3.0720, 0.0166,-1.8427,-0.0029,-1.2515],
    [2.7770, 0.0100, 1.7292,-0.0131,-0.9675],
    [5.4923,-0.0071,-6.4753,-0.0067, 0.9119],
    [3.2497, 0.0088, 2.3223,-0.0069,-0.8778],
    [4.4449, 0.0091, 4.8613,-0.0138, 0.5910]
    ]
constants = constants_1


# Inertia: B=1/2I
m = 1.00784  # H
r = 0.6  # APROX... NEEDS TO BE CHANGED
B = 1.0 / 2 * 3*(m * r**2)
# Grid
N = 30
x = np.linspace(0, 2*np.pi, N)
dx = x[1] - x[0]


# Hamiltonian built by finite difference method, with periodic B.C.
#          [  2 -1  0  0  1 ]           [ V(0)                ]
#          [ -1  2 -1  0  0 ]           [    V(1)             ]
# H = -B * [  0 -1  2 -1  0 ] / dx**2 + [        V(2)         ]
#          [  0  0 -1  2 -1 ]           [            V(3)     ]
#          [  1  0  0 -1  2 ]           [                V(4) ]
finite_difference_matrix = Matrix(N, N, lambda i, j: 1 if abs(i-j) == 1 else -2 if i == j else 1 if abs(i-j) == N-1 else 0)
#print(finite_difference_matrix)


time_start = time.time()

energies = []
for C in constants:
    # Potential energy vector
    U_list = []
    for angle in x:
        U_list.append(V(angle, C))
    U = Matrix(N, N, lambda i, j: U_list[i] if i == j else 0)
    # Solve Hamiltoninan eigenvalues and eigenvectors
    H = -B * finite_difference_matrix / dx**2 + U
    eigenvalues = H.eigenvals()
    eigenvalues_list = list(eigenvalues)
    eigenvalues_sorted = sorted(eigenvalues_list)
    print('Eigenvalues:')
    print(eigenvalues_sorted)
    energies.append(eigenvalues_sorted)

time_end = time.time() - time_start
print(f'Computation time: {time_end:.2f} seconds')


# Plot potential energy and energy eigenvalues
for C, eigenvalues in zip(constants, energies):
    # Plot potential energy
    plt.figure(figsize=(10, 6))
    plt.plot(x, V(x, C), label='Potential')
    plt.xlabel('Angle / radians')
    plt.ylabel('Energy / meV')
    plt.title('Hindered methyl rotor potential')
    # Plot energy eigenvalues
    for i in range(len(eigenvalues)):
        plt.axhline(y=eigenvalues[i], color='r', linestyle='-')
        plt.text(i%2, eigenvalues[i], f'E = {eigenvalues[i]:.4f}', va='bottom')
    plt.legend()
    plt.show()

