import qrotor as qr
import aton


folder = 'tests/samples/'
structure = folder + 'CH3NH3.in'
structure_120 = folder + 'CH3NH3_120.in'
structure_60 = folder + 'CH3NH3_60.in'


def test_save_and_load():
    system = qr.System()
    system.gridsize = 36
    system.potential_name = 'sin'
    system.B = 1
    system.solve_potential()
    potential_file = folder + '_temp_potential.csv'
    # Remove the file if it exists
    try:
        aton.file.remove(potential_file)
    except:
        pass
    qr.potential.save(system, comment='hi', filepath=potential_file)
    system_new = qr.potential.load(potential_file)
    assert system_new.gridsize == system.gridsize
    assert round(system_new.potential_values[0], 5) == round(system.potential_values[0], 5)
    assert round(system_new.potential_values[5], 5) == round(system.potential_values[5], 5)
    assert round(system_new.potential_values[13], 5) == round(system.potential_values[13], 5)
    assert system_new.comment == 'hi'
    aton.file.remove(potential_file)
    # If we don't provide a comment, it should be the name of the folder
    system.comment = None
    qr.potential.save(system, filepath=potential_file)
    system_new = qr.potential.load(potential_file)
    assert system_new.comment == 'samples'
    aton.file.remove(potential_file)

