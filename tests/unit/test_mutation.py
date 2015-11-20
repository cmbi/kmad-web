from nose.tools import eq_

from kmad_web.domain.mutation import Mutation


def test_mutation():
    s = {'seq': 'ABCA', 'aligned': '-ABC-A'}
    m = Mutation(s, 4, 'C')

    eq_(5, m.alignment_position)
    eq_('ABCC', m.mutant_sequence)
    eq_(3, m.position)
