import qrotor as qr
import numpy as np


def test_phase():
    sys = qr.System()
    sys.B = 1.0
    sys.potential_name = 'cos'
    sys.gridsize = 10000
    sys.solve()
    # plus pi/2, which will be -3pi/2
    sys.change_phase(0.5)
    assert round(sys.grid[0], 2) == round(-np.pi * 3/2, 2)
    # The first potential value should be 0,
    # but remember that the potential offset is corrected
    # so it should be half potential_max, so 1.0/2
    assert round(sys.potential_values[0], 2) == 0.5
    # minus pi, which will become -pi/2
    sys.change_phase(-1)
    assert round(sys.grid[0], 2) == round(-np.pi/2, 2)
    assert round(sys.potential_values[0], 2) == 0.5
    # Were eigenvalues calculated?
    assert len(sys.eigenvalues) > 0

