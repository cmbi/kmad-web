from mock import patch
from nose.tools import eq_, ok_


def test_create_mutant_sequence():

    from kmad_web.services.mutation_analysis import create_mutant_sequence

    seq = "SEQ"
    mutation_site = 1
    new_aa = "P"
    result = create_mutant_sequence(seq, mutation_site, new_aa)
    expected = "SPQ"
    eq_(expected, result)
