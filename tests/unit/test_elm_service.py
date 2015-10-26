import json
import requests

from mock import patch, Mock
from nose.tools import eq_, assert_raises

from kmad_web.services.elm import ElmService
from kmad_web.services.types import ServiceError


@patch('requests.get')
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
def test_get_instances_failure(mock_requests_get):
    mock_requests_get.side_effect = requests.HTTPError
    test_id = "TAU_HUMAN"
    url = "http://elm.eu.org/"
    elm = ElmService(url=url)
    assert_raises(ServiceError, elm.get_instances, test_id)

def test_get_motif_go_terms():
    test_id = "MOD_PIKK_1"
    elm = ElmService("http://elm.eu.org/")
    expected = ['0006975', '0000077', '0016447', '0005634', '0004674']
    eq_(expected, elm.get_motif_go_terms(test_id))
