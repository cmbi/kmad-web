import xmltodict
import requests
import requests_mock

from mock import patch, Mock
from nose.tools import eq_, assert_raises, with_setup

from kmad_web.services.pfam import PfamService
from kmad_web.services.types import ServiceError, TimeoutError
from kmad_web.services.helpers.cache import cache_manager as cm


def setup():
    cm.load_config({
        'redis': {'redis.backend': 'dogpile.cache.null'}
    })


def teardown():
    cm.reset()


@patch('kmad_web.services.pfam.requests.post')
@patch('kmad_web.services.pfam.requests.get')
@with_setup(setup, teardown)
def test_search_success(mock_requests_get, mock_requests_post):

    mock_response_post = Mock()
    mock_response_post.text = "<jobs>\n<job>\n<result_url>test_url" \
                              "</result_url>\n</job>\n</jobs>\n"
    mock_requests_post.return_value = mock_response_post

    expected_result = "<?xml blabla >"
    mock_response_get = Mock()
    mock_response_get.text = expected_result
    mock_requests_get.return_value = mock_response_get

    test_seq = ">test_seq\nABCD\n"
    url = "http://pfam.xfam.org/search/sequence"
    pfam = PfamService(url=url)
    result = pfam.search(test_seq)
    eq_(expected_result, result)


@with_setup(setup, teardown)
@requests_mock.Mocker()
def test_search(mock_requests):
    test_seq = ">test_seq\nABCD\n"
    url = "http://pfam_url"

    dict_response = {'jobs': {'job': {'result_url': 'http://test_url'}}}
    xml_response = xmltodict.unparse(dict_response)

    mock_requests.register_uri('POST', url, text=xml_response)
    mock_requests.register_uri('GET', 'http://test_url',
                               text="<?xml pfam_result")
    pfam = PfamService(url=url)
    eq_("<?xml pfam_result", pfam.search(test_seq))


# @patch('kmad_web.services.pfam.requests.post')
# @patch('kmad_web.services.pfam.requests.get')
# @with_setup(setup, teardown)
# def test_search_failure(mock_requests_get, mock_requests_post):
#
#     from kmad_web.services.pfam import PfamService
#     from kmad_web.services.types import ServiceError
#
#     mock_requests_post.side_effect = requests.HTTPError
#
#     test_seq = ">test_seq\nABCD\n"
#     url = "http://pfam.xfam.org/search/sequence"
#     pfam = PfamService(url=url)
#     assert_raises(ServiceError, pfam.search, test_seq)

@with_setup(setup, teardown)
@requests_mock.Mocker()
def test_search_failure(mock_requests):
    test_seq = ">test_seq\nABCD\n"
    url = "http://pfam_url"
    mock_requests.register_uri('POST', url, text='bad_response')
    pfam = PfamService(url=url)
    assert_raises(ServiceError, pfam.search, test_seq)

    dict_response = {'jobs': {'job': {'result_url': 'http://test_url'}}}
    xml_response = xmltodict.unparse(dict_response)

    mock_requests.register_uri('POST', url, text=xml_response)
    mock_requests.register_uri('GET', 'http://test_url',
                               text="not xml")
    pfam = PfamService(url=url)
    assert_raises(TimeoutError, pfam.search, test_seq, 1, 1)


@patch('kmad_web.services.pfam.requests.get')
def test_status_failure(mock_get):
    url = "http://pfam_status_url"
    pfam = PfamService(url=url)
    mock_get.side_effect = requests.HTTPError
    assert_raises(ServiceError, pfam._status, url)


@patch('kmad_web.services.pfam.requests.post')
def test_create_failure(mock_post):
    url = "http://pfam_create_url"
    pfam = PfamService(url=url)
    mock_post.side_effect = requests.HTTPError
    assert_raises(ServiceError, pfam._create, url)
