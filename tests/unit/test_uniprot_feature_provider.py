from nose.tools import eq_, ok_, with_setup

from kmad_web.services.helpers.cache import cache_manager as cm
from kmad_web.domain.features.providers.uniprot import UniprotFeatureProvider


def setup():
    cm.load_config({
        'redis': {'redis.backend': 'dogpile.cache.null'}
    })


def teardown():
    cm.reset()


@with_setup(setup, teardown)
def test_get_ptms():
    uniprot = UniprotFeatureProvider()
    p = uniprot.get_ptms('TAU_HUMAN')
    ok_(p)


def test_get_ptm_type():
    ptm_name = "Phosphoserine; by PDPK1 and TTBK1."
    expected_type = 'phosphorylation'
    uniprot = UniprotFeatureProvider()
    eq_(expected_type, uniprot._get_ptm_type(ptm_name))
