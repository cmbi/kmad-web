import json
import requests

from mock import patch, Mock
from nose.tools import eq_, assert_raises


@patch('requests.get')
def test_get_instances_success(mock_requests_get):

    from kmad_web.services.elm import ElmService

    mock = Mock(spec=requests.Response)
    mock.status_code = 200
    mock.text = json.dumps({'result': 'ELM result'})
    mock_requests_get.return_value = mock

    test_id = "TAU_HUMAN"
    url = "http://elm.eu.org/instances.gff?q={}".format(test_id)
    elm = ElmService(url=url)
    result = elm.get_instances()

    eq_(result, '{"result": "ELM result"}')


@patch('requests.get')
def test_get_instances_failure(mock_requests_get):

    from kmad_web.services.elm import ElmService
    from kmad_web.services.types import ServiceError

    mock_requests_get.side_effect = requests.HTTPError
    test_id = "TAU_HUMAN"
    url = "http://elm.eu.org/instances.gff?q={}".format(test_id)
    elm = ElmService(url=url)
    assert_raises(ServiceError, elm.get_instances)
