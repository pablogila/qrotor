import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh
import matplotlib.pyplot as plt
import time
import matplotlib.ticker as ticker


# The Hamiltonian is built via finite difference method, with periodic B.C.
#          [  2 -1  0  0  1 ]           [ V(0)                ]
#          [ -1  2 -1  0  0 ]           [    V(1)             ]
# H = -B * [  0 -1  2 -1  0 ] / dx**2 + [        V(2)         ]
#          [  0  0 -1  2 -1 ]           [            V(3)     ]
#          [  1  0  0 -1  2 ]           [                V(4) ]


# Potential energy function of the hindered methyl rotor, from titov2023
def V(x, C):
    return C[0] + C[1] * np.sin(3*x) + C[2] * np.cos(3*x) + C[3] * np.sin(6*x) + C[4] * np.cos(6*x)


# Second derivative matrix, according to the finite difference method
def second_derivative_matrix(x):
    diagonals = [-2*np.ones(len(x)), np.ones(len(x)-1), np.ones(len(x)-1)]
    second_derivative_matrix = diags(diagonals, [0, -1, 1]).toarray()
    # Periodic boundary conditions
    second_derivative_matrix[0, -1] = 1
    second_derivative_matrix[-1, 0] = 1
    dx = x[1] - x[0]
    second_derivative_matrix /= dx**2
    return second_derivative_matrix


# Solve the Hamiltonian eigenvalues for the time independent Schrödinger equation
def solve_energies(potential, B, x, searched_energies=5):
    # Solve Hamiltoninan eigenvalues
    H = -B * second_derivative_matrix(x) + diags(potential)
    eigenvalues, _ = eigsh(H, searched_energies, which='SM')  # Omit the eigenvectors with '_'
    return eigenvalues


# Potential constants from titov2023 [C1, C2, C3, C4, C5]
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
# Choose the set of constants to use
constants = constants_1


# Number of energy levels to calculate
searched_energies = 7
# Inertia: B=1/2I
m_H = 1.00784      # H mass
m_D = 2.014102     # D mass
r = 0.62  # 1.035  # Measured value??  # It should be around 0.6 ???
B = 1.0 / 2 * 3*(m_H * r**2)
#B = 0.574  # From titov2023
# Grid size
N = 500
x = np.linspace(0, 2*np.pi, N)


time_start = time.time()

energies = []
for C in constants:
    U = V(x, C)
    eigenvalues = solve_energies(U, B, x, searched_energies)
    energy_barrier = max(U) - min(eigenvalues)

    print(eigenvalues)
    print(f'Energy barrier: {energy_barrier:.4f} meV')
    energies.append(eigenvalues)

time_end = time.time() - time_start
print(f'Computation time: {time_end:.2f} seconds')


# Plots
for C, eigenvalues in zip(constants, energies):
    # Plot potential energy
    plt.figure(figsize=(10, 6))
    plt.plot(x, V(x, C))
    plt.xlabel('Angle / radians')
    plt.ylabel('Energy / meV')
    plt.title('Hindered methyl rotor potential (#' + str(constants.index(C)+1) + ')' )
    # Plot energy eigenvalues
    for i in range(len(eigenvalues)):
        plt.axhline(y=eigenvalues[i], color='r')
        plt.text(i%3, eigenvalues[i], f'E$_{i}$ = {eigenvalues[i]:.4f}', va='center', bbox=dict(edgecolor='lightgrey', boxstyle='round,pad=0.2', facecolor='white', alpha=1))
    plt.xticks([0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi],
               ['0', r'$\frac{\pi}{2}$', r'$\pi$', r'$\frac{3\pi}{2}$', r'$2\pi$'])
    plt.show()

