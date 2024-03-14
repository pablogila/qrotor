import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp






# potential from titov2023
C0 = [2.7860, 0.0130, -1.5284, -0.0037, -1.2791]
C1 = [2.6507, 0.0158, -1.4111, -0.0007, -1.2547]
C2 = [2.1852, 0.0164, -1.0017, 0.0003, -1.2061]
C3 = [5.9109, 0.0258, -7.0152, -0.0168, 1.0213]
C4 = [1.4526, 0.0134, -0.3196, 0.0005, -1.1461]
constants = [C0, C1, C2, C3, C4]




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
plt.legend(['0', '1', '2', '3', '4']).set_title('Potentials\ntitov2023')
plt.show()


# Inertia: B=1/2I
m = 1.00784
r = 1.0  # CHECK
B = 1.0 / 2 * 3*(m * r**2)
# Grid parameters
L = 2*np.pi  # Periodicity
N = 200  # Number of grid points
dx = L / N  # Grid spacing
x = np.linspace(0, L, N)  # Create grid




def harmonic_oscillator (t, Y, omega):
    y, ydot = Y
    return ydot, -omega**2 * y


# For the Harmonic Oscillator
L = 2*np.pi  # Size / Periodicity
N = 200  # Number of grid points
dt = L / N  # Grid spacing
t = np.linspace(0, L, N)  # Create grid

# solve for omega=2
sol = solve_ivp(harmonic_oscillator, [0,2*np.pi], [1,0], t_eval=t, args=(2,))

print(sol)

plt.plot(sol.t, sol.y[0], label=r'$y$')
plt.plot(sol.t, sol.y[1], label=r'$\dot {y }$')
plt.xlabel('t')
plt.title('Harmonic Oscillator:  $\ddot {y } (t) + \omega² y(t) = 0$,  $\omega = 2$')
plt.legend()
plt.show()










