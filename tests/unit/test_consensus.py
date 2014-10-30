from nose.tools import eq_


def test_find_consensus_disorder():
    from kman_web.services.consensus import find_consensus_disorder

    in_data = [['1', [0, 0, 0, 0]],
               ['2', [0, 0, 0, 2]],
               ['3', [0, 0, 2, 2]],
               ['4', [0, 2, 2, 2]]]

    expected = ['consensus', [0, 0, 1, 2]]

    eq_(find_consensus_disorder(in_data), expected)


def test_filter_out_short_stretches():
    from kman_web.services.consensus import filter_out_short_stretches

    in_data = [0, 0, 0, 2, 0, 0, 0, 1, 0, 1, 0, 0, 1]
    expected = ['filtered', [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0]]

    eq_(filter_out_short_stretches(in_data), expected)
