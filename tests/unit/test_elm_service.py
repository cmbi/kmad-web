import json
import requests
import requests_mock

from mock import patch, Mock
from nose.tools import eq_, assert_raises, with_setup

from kmad_web.services.elm import ElmService
from kmad_web.services.types import ServiceError
from kmad_web.services.helpers.cache import cache_manager as cm


def setup():
    cm.load_config({
        'redis': {'redis.backend': 'dogpile.cache.null'}
    })


def teardown():
    cm.reset()


@patch('requests.get')
@with_setup(setup, teardown)
def test_get_instances_success(mock_requests_get):
    mock = Mock(spec=requests.Response)
    mock.status_code = 200
    mock.text = json.dumps({'result': 'ELM result'})
    mock_requests_get.return_value = mock

    test_id = "TAU_HUMAN"
    url = "http://elm.eu.org/"
    elm = ElmService(url=url)
    result = elm.get_instances(test_id)

    eq_(result, '{"result": "ELM result"}')


@patch('requests.get')
@with_setup(setup, teardown)
def test_get_instances_failure(mock_requests_get):
    mock_requests_get.side_effect = requests.HTTPError
    test_id = "TAU_HUMAN"
    url = "http://elm.eu.org/"
    elm = ElmService(url=url)
    assert_raises(ServiceError, elm.get_instances, test_id)


@with_setup(setup, teardown)
def test_get_motif_go_terms():
    test_id = "MOD_PIKK_1"
    elm = ElmService("http://elm.eu.org/")
    expected = set(['0006975', '0000077', '0016447', '0005634', '0004674'])
    eq_(expected, elm.get_motif_go_terms(test_id))


@with_setup(setup, teardown)
@requests_mock.Mocker()
def test_get_all_classes(mock_requests):
    url = "http://elm.eu.org/elms/elms_index.tsv"
    mock_requests.register_uri('GET', url, text='all classes')
    elm = ElmService("http://elm.eu.org/")
    elm.get_all_classes()
    mock_requests.register_uri('GET', url, text='all classes', status_code=404)
    assert_raises(ServiceError, elm.get_all_classes)
