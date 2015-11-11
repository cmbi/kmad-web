import json
import requests

from mock import patch, Mock
from nose.tools import eq_, assert_raises, with_setup
from kmad_web.services.helpers.cache import cache_manager as cm


def setup():
    cm.load_config({
        'redis': {'redis.backend': 'dogpile.cache.null'}
    })


def teardown():
    cm.reset()


@patch('requests.get')
@with_setup(setup, teardown)
def test_get_fasta_success(mock_requests_get):

    from kmad_web.services.uniprot import UniprotService

    mock = Mock(spec=requests.Response)
    mock.status_code = 200
    mock.text = json.dumps({'result': 'Uniprot result'})
    mock_requests_get.return_value = mock

    test_id = "TAU_HUMAN"
    url = "http://uniprot.org/uniprot/"
    uniprot = UniprotService(url=url)
    result = uniprot.get_fasta(test_id)

    eq_(result, '{"result": "Uniprot result"}')


@patch('requests.get')
@with_setup(setup, teardown)
def test_get_fasta_failure(mock_requests_get):

    from kmad_web.services.uniprot import UniprotService
    from kmad_web.services.types import ServiceError

    mock_requests_get.side_effect = requests.HTTPError
    test_id = "TAU_HUMAN"
    url = "http://uniprot.org/uniprot/"
    uniprot = UniprotService(url=url)
    assert_raises(ServiceError, uniprot.get_fasta, test_id)


@patch('requests.get')
@with_setup(setup, teardown)
def test_get_txt_success(mock_requests_get):

    from kmad_web.services.uniprot import UniprotService

    mock = Mock(spec=requests.Response)
    mock.status_code = 200
    mock.text = json.dumps({'result': 'Uniprot result'})
    mock_requests_get.return_value = mock

    test_id = "TAU_HUMAN"
    url = "http://uniprot.org/uniprot/"
    uniprot = UniprotService(url=url)
    result = uniprot.get_txt(test_id)

    eq_(result, '{"result": "Uniprot result"}')


@patch('requests.get')
@with_setup(setup, teardown)
def test_get_txt_failure(mock_requests_get):

    from kmad_web.services.uniprot import UniprotService
    from kmad_web.services.types import ServiceError

    mock_requests_get.side_effect = requests.HTTPError
    test_id = "TAU_HUMAN"
    url = "http://uniprot.org/uniprot/"
    uniprot = UniprotService(url=url)
    assert_raises(ServiceError, uniprot.get_txt, test_id)
