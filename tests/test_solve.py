import qrotor as qr


def test_solve_zero():
    system = qr.System()
    system.gridsize = 50000
    system.potential_name = 'zero'
    system.B = 1
    system.solve()
    assert round(system.eigenvalues[0], 2) == 0.0
    assert round(system.eigenvalues[1], 2) == 1.0
    assert round(system.eigenvalues[2], 2) == 1.0
    assert round(system.eigenvalues[3], 2) == 4.0
    assert round(system.eigenvalues[4], 2) == 4.0
    assert round(system.eigenvalues[5], 2) == 9.0
    assert round(system.eigenvalues[6], 2) == 9.0
    assert round(system.eigenvalues[7], 2) == 16.0
    assert round(system.eigenvalues[8], 2) == 16.0


def test_solve_potential():
    system = qr.System()
    system.gridsize = 500
    system.potential_name = 'sin'
    system.potential_constants = [0, 1, 3, 0]
    system.solve_potential()
    assert round(system.potential_max, 2) == 1.0

def test_degeneracy_fail_point():
    import numpy as np
    from qrotor.system import System
    degrees = np.arange(0, 360, 10)
    energies = (1-np.cos(3*np.radians(degrees - 30.)))*2 + np.sin(20*np.radians(degrees - 30.))
    energies -= np.min(energies)
    system = System()
    positions = np.radians(degrees)
    potentials = np.array(energies) * 10
    system.grid = np.array(positions)
    system.gridsize = len(positions)
    system.potential_values = np.array(potentials)
    system.searched_E = 10
    system.solve(500)
    assert round(system.eigenvalues[0], 0) == 16

