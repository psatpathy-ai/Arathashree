from arthashree.risk import position_size

def test_position_size_respects_risk():
    q = position_size(1_000_000, 100, 90, 0.01)
    assert q == 1000

def test_no_zero_stop_distance():
    assert position_size(1_000_000, 100, 100, 0.01) == 0
