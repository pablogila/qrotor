import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp # Initial value problems


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

