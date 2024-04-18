from .common import *


# Output file
filename = 'QRotor_OUT'
logfile = os.path.join(os.getcwd(), filename)


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

constants_titov2023 = [
    [2.7860, 0.0130,-1.5284,-0.0037,-1.2791],
    [2.6507, 0.0158,-1.4111,-0.0007,-1.2547],
    [2.1852, 0.0164,-1.0017, 0.0003,-1.2061],
    [5.9109, 0.0258,-7.0152,-0.0168, 1.0213],
    [1.4526, 0.0134,-0.3196, 0.0005,-1.1461]
    ]


# Default testing variables object
test_variables = Variables()
test_variables.set_of_constants = constants_titov2023 #constants_titov_1
test_variables.potential_name = 'titov2023'  # 'titov2023' or 'zero'
test_variables.atom_type = 'H'
test_variables.B = B_Hydrogen
test_variables.searched_E_levels = 5
test_variables.gridsize = 100
test_variables.grid = np.linspace(0, 2*np.pi, test_variables.gridsize)
test_variables.write_summary = True

