from nose.tools import eq_

from kmad_web.domain.go.providers.uniprot import UniprotGoTermProvider

def test_get_go_terms():
    test_id = 'Q9SQZ9'
    uniprot = UniprotGoTermProvider()
    expected = ['0005623', '0015035', '0045454', '0006662']
    eq_(expected, uniprot.get_go_terms(test_id))
