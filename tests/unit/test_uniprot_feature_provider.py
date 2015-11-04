from nose.tools import eq_, ok_
from kmad_web.domain.features.providers.uniprot import UniprotFeatureProvider


def test_get_ptms():
    uniprot = UniprotFeatureProvider()
    p = uniprot.get_ptms('TAU_HUMAN')
    ok_(p)


def test_get_ptm_type():
    ptm_name = "Phosphoserine; by PDPK1 and TTBK1."
    expected_type = 'phosphorylation'
    uniprot = UniprotFeatureProvider()
    eq_(expected_type, uniprot._get_ptm_type(ptm_name))
