from mock import patch, PropertyMock
from nose.tools import eq_

from kmad_web.domain.features.providers.pfam import PfamFeatureProvider


@patch('kmad_web.domain.features.providers.pfam.PfamParser')
@patch('kmad_web.domain.features.providers.pfam.PfamService')
def test_get_domains(mock_service, mock_parser):
    pfam_provider = PfamFeatureProvider()

    type(mock_parser.return_value).domains = PropertyMock(
        return_value=[{
            'accession': 'test_acc',
            'ali_start': '0',
            'ali_end': '0',
            'some_other_key': 'test'
        }])

    expected = [{
        'accession': 'test_acc',
        'start': '0',
        'end': '0'
    }]

    eq_(expected, pfam_provider.get_domains(
        {'header': '>1', 'seq': 'SEQ', 'id': 'seq_id'}))
