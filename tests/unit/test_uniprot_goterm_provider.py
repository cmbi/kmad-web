from mock import patch
from nose.tools import eq_, with_setup

from kmad_web.domain.go.providers.uniprot import UniprotGoTermProvider
from kmad_web.services.helpers.cache import cache_manager as cm


def setup():
    cm.load_config({
        'redis': {'redis.backend': 'dogpile.cache.null'}
    })


def teardown():
    cm.reset()


@patch('kmad_web.domain.go.providers.uniprot.UniprotService.get_txt')
@with_setup(setup, teardown)
def test_get_go_terms(mock_get_txt):
    mock_get_txt.return_value = open('tests/unit/testdata/test.txt').read()
    test_id = 'Q9SQZ9'
    uniprot = UniprotGoTermProvider()
    expected = ['0030424', '0005930']
    eq_(expected, uniprot.get_go_terms(test_id))
