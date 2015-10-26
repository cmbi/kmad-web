from mock import patch
from nose.tools import eq_

from kmad_web.domain.features.providers.netphos import NetphosFeatureProvider

@patch('kmad_web.services.netphos.NetphosService.predict')
def test_get_phosphorylations(mock_predict):
    with open('tests/unit/testdata/netphos_result') as a:
        mock_predict.return_value = a.read()

    netphos = NetphosFeatureProvider()
    netphos.get_phosphorylations('test_filename')
    expected_result = [{'positions': 8,
                        'annotation_level': 4,
                        'name': 'phosphorylation'
                        },
                       {'positions': 34,
                        'annotation_level': 4,
                        'name': 'phosphorylation'
                        },
                       {'positions': 55,
                        'annotation_level': 4,
                        'name': 'phosphorylation'
                        }]
    eq_(netphos.phosphorylations, expected_result)

