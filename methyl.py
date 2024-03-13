import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import eigsh


# potential from titov2023
C0 = [2.7860, 0.0130, -1.5284, -0.0037, -1.2791]
C1 = [2.6507, 0.0158, -1.4111, -0.0007, -1.2547]
C2 = [2.1852, 0.0164, -1.0017, 0.0003, -1.2061]
C3 = [5.9109, 0.0258, -7.0152, -0.0168, 1.0213]
C4 = [1.4526, 0.0134, -0.3196, 0.0005, -1.1461]
constants = [C0, C1, C2, C3, C4]

# hydrogen mass
m = 1.00784  # amu
# Methyl radious
r = 1.0  # Angstrom


def potential(angle, C = C0):
    V = C[0] + C[1] * np.sin(3*angle) + C[2] * np.cos(3*angle) + C[3] * np.sin(6*angle) + C[4] * np.cos(6*angle)
    return V


for constant in constants:
    angles = np.linspace(-np.pi, np.pi, 1000)
    potentials = potential(angles, constant)
    plt.plot(angles, potentials)


plt.xlabel('Angle / radians')
plt.ylabel('Potential / meV')
plt.title('Hindered methyl rotor potential')
plt.legend(['0', '1', '2', '3', '4']).set_title('From titov2023')
plt.show()


B = 1.0 / 2 * 3*(m * r**2)


# Grid parameters
a = 2*np.pi  # Periodic boundary condition: length of the box
N = 200  # Number of grid points
dx = a / (N - 1)  # Grid spacing

# Create grid
x = np.linspace(0, a, N)

# Discretize kinetic energy operator using second-order central difference
d2psi = -B / (dx**2) * (np.roll(np.eye(N), -1, axis=0) + np.roll(np.eye(N), 1, axis=0) - 2*np.eye(N))

# Build Hamiltonian matrix (including potential)
H = d2psi + np.diag(potential(x))

# Solve eigenvalue problem with periodic boundary conditions
# Enforce zero derivative at boundaries (Neumann)
d2psi_ends = np.zeros((2, N))
d2psi_ends[0, 1:-1] = -2*B/dx**2
d2psi_ends[1, :-1] = 2*B/dx**2
H_periodic = H - d2psi_ends[0] - d2psi_ends[1]

# Find a few lowest eigenvalues and eigenvectors
eigenvalues, eigenvectors = eigsh(H_periodic, k=5, which='SM')

# Print results
print("Eigenvalues (first 5):", eigenvalues)
# You can analyze the eigenvectors for the wave function information

