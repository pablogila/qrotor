import qrotor as qr


def test_constants():
    assert round(qr.B_CH3, 5) == 0.64518
    assert round(qr.B_CD3, 5) == 0.32289
    assert round(qr.B_NH3, 5) == 0.73569
    assert round(qr.B_ND3, 5) == 0.36819
    assert round(qr.Ry_to_eV, 5)  == 13.60569
    assert round(qr.Ry_to_meV, 5) == 13605.69312
    assert round(qr.eV_to_Ry, 5)  == 0.07350
    assert round(qr.meV_to_Ry, 10) == .0000734986

