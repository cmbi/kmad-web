import requests

from mock import patch, Mock
from nose.tools import eq_, assert_raises

from kmad_web.services.pfam import PfamService


@patch('kmad_web.services.pfam.requests.post')
@patch('kmad_web.services.pfam.requests.get')
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
    eq_([expected_result], result)


@patch('kmad_web.services.pfam.requests.post')
@patch('kmad_web.services.pfam.requests.get')
def test_search_failure(mock_requests_get, mock_requests_post):

    from kmad_web.services.pfam import PfamService
    from kmad_web.services.types import ServiceError

    mock_requests_post.side_effect = requests.HTTPError

    test_seq = ">test_seq\nABCD\n"
    url = "http://pfam.xfam.org/search/sequence"
    pfam = PfamService(url=url)
    assert_raises(ServiceError, pfam.search, test_seq)


def test_actual():
    test_seq = ">test_seq\nMAPAADMTSLPLGVKVEDSAFGKPAGGGAGQAPSAAAATAAAMGADEEGAKPKVSPSLLP\n"
    url = "http://pfam.xfam.org/search/sequence"
    pfam = PfamService(url=url)
    result = pfam.search(test_seq)
    assert(False)
