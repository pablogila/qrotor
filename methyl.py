import numpy as np
import matplotlib.pyplot as plt


# potential from titov2023
C = [2.7860, 0.0130, -1.5284, -0.0037, -1.2791]
def potential(angle):
    V = C[0] + C[1] * np.sin(3*angle) + C[2] * np.cos(3*angle) + C[3] * np.sin(6*angle) + C[4] * np.cos(6*angle)
    return V


angles = np.linspace(-np.pi, np.pi, 1000)
potentials = potential(angles)

plt.plot(angles, potentials)
plt.xlabel('Angle / radians')
plt.ylabel('Potential / a.u.')
plt.title('Hindered methyl rotor potential')
plt.show()

