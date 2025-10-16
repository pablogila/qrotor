import qrotor as qr


def test_tags():
    sys1 = qr.System(tags='tag1 tag2 tag3', comment='sys1', potential_name='zero')
    sys2 = qr.System(tags='tag2 tag3 tag4', comment='sys2')
    sys3 = qr.System(tags='tag4 tag5 tag6', comment='sys3')
    sys1.solve(100)
    test1 = qr.systems.filter_tags(sys1, include='tag4')
    assert test1 == []
    test2 = qr.systems.filter_tags([sys1, sys2], include='tag4 tag5', strict=False)
    assert len(test2) == 1
    assert test2[0].comment == 'sys2'
    test3 = qr.systems.filter_tags([sys1, sys2], include='tag4 tag5', strict=True)
    assert test3 == []
    test4 = qr.systems.filter_tags([sys1, sys2, sys3], include='tag3 tag4', strict=False)
    assert len(test4) == 3
    test5 = qr.systems.filter_tags([sys1, sys2, sys3], include='tag3 tag4', strict=True)
    assert len(test5) == 1
    assert test5[0].comment == 'sys2'
    test6 = qr.systems.filter_tags([sys1, sys2, sys3], include='tag3 tag4', exclude='tag6', strict=False)
    assert len(test6) == 2
    test7 = qr.systems.filter_tags([sys1, sys2, sys3], include='tag4', exclude='tag5 tag6', strict=True)
    assert len(test7) == 1
    assert test7[0].comment == 'sys2'
    test8 = qr.systems.filter_tags([sys1, sys2, sys3], include='', exclude='tag1 tag2', strict=True)
    assert len(test8) == 2
    test9 = qr.systems.filter_tags([sys1, sys2, sys3], include='', exclude='tag1 tag2', strict=False)
    assert test9[0].comment == 'sys3'

