from nose.tools import ok_, with_setup

from kmad_web.parsers.uniprot import UniprotParser
from kmad_web.services.uniprot import UniprotService
from kmad_web.domain.features.providers.uniprot import UniprotFeatureProvider
from kmad_web.default_settings import UNIPROT_URL
from kmad_web.services.helpers.cache import cache_manager as cm


def setup():
    cm.load_config({
        'redis': {'redis.backend': 'dogpile.cache.null'}
    })


def teardown():
    cm.reset()


@with_setup(setup, teardown)
def test_xml():
    p = UniprotParser()
    s = UniprotService(UNIPROT_URL)
    uni_xml = s.get_xml("P21815")
    p.parse_ptms_xml(uni_xml)
    ok_(p.ptms)


@with_setup(setup, teardown)
def test_fetaure_provider():
    p = UniprotFeatureProvider()
    ok_(p.get_ptms("P21815"))
