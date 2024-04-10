from qrotor.core import *


# Output file
filename = 'output.txt'
out_file = os.path.join(os.getcwd(), filename)


# Atomic masses
m_H = 1.00784      # H mass
m_D = 2.014102     # D mass
# Methyl rotor radius
r = 0.537  # in ¿meV?  # 1.035 angstroms for MAI... CHECK UNITS
# Inertia. Should be 0.574 for H, according to titov2023
B_Hydrogen = 1.0 / (2 * 3*(m_H * r**2))
B_Deuterium = 1.0 / (2 * 3*(m_D * r**2))


# Potential constants from titov2023 [C1, C2, C3, C4, C5]
constants_zero = [
    [0,0,0,0,0]
    ]
constants_titov_1 = [
    [2.7860, 0.0130,-1.5284,-0.0037,-1.2791],
    [2.6507, 0.0158,-1.4111,-0.0007,-1.2547],
    [2.1852, 0.0164,-1.0017, 0.0003,-1.2061],
    [5.9109, 0.0258,-7.0152,-0.0168, 1.0213],
    [1.4526, 0.0134,-0.3196, 0.0005,-1.1461]
    ]
constants__titov_2 = [
    [2.7860, 0.0130,-1.5284,-0.0037,-1.2791],
    [3.0720, 0.0166,-1.8427,-0.0029,-1.2515],
    [2.7770, 0.0100, 1.7292,-0.0131,-0.9675],
    [5.4923,-0.0071,-6.4753,-0.0067, 0.9119],
    [3.2497, 0.0088, 2.3223,-0.0069,-0.8778],
    [4.4449, 0.0091, 4.8613,-0.0138, 0.5910]
    ]


# Instantiate objects. These are used to pass data between functions.
variables = Variables()


# Choose the default set of constants to use
variables.set_of_constants = constants_titov_1 #constants_titov_1
variables.potential_name = 'titov2023'  # 'titov2023' or 'zero'
# Number of energy levels to calculate
variables.searched_E_levels = 5
# Grid size
variables.N = 100
variables.x = np.linspace(0, 2*np.pi, variables.N)

