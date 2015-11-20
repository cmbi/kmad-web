from mock import patch
from nose.tools import eq_

from kmad_web.domain.features.providers.elm import ElmFeatureProvider


def test_filter_motifs():
    test_motifs = [{'start': 1, 'end': 5, 'probability': 0.5},
                   {'start': 2, 'end': 4, 'probability': 0.5},
                   {'start': 5, 'end': 8, 'probability': 0.3},
                   {'start': 5, 'end': 8, 'probability': 0.8},
                   {'start': 5, 'end': 8, 'probability': 0.8},
                   ]
    expected_motifs = [{'start': 2, 'end': 4, 'probability': 0.5},
                       {'start': 5, 'end': 8, 'probability': 0.8}]
    elm = ElmFeatureProvider('test_path')
    eq_(expected_motifs, elm.filter_motifs(test_motifs))


@patch('kmad_web.domain.features.providers.elm.ElmService')
def test_get_motif_instances(mock_service):
    test_id = "test_id"
    seq = "KDEL"

    elm = ElmFeatureProvider(['GO:0031873'])
    expected_id = 'TRG_ER_KDEL_1'
    result = elm.get_motif_instances(seq, test_id)

    eq_(1, len(result))
    eq_(expected_id, result[0]['id'])


def test_get_more_info():
    test_inst = [
        {'start': 1, 'end': 2, 'id': 'test_id1'},
        {'start': 1, 'end': 2, 'id': 'test_id2'},
    ]

    full_classes = {
        'test_id1': {
            'class': 'test_class1', 'probability': 'p', 'pattern': 'p'
        },
        'test_id2': {
            'class': 'test_class2', 'probability': 'p', 'pattern': 'p'
        }
    }
    expected = [
        {'start': 1, 'end': 2, 'id': 'test_id1', 'pattern': 'p',
         'probability': 1, 'class': 'test_class1'},
        {'start': 1, 'end': 2, 'id': 'test_id2', 'pattern': 'p',
         'probability': 1, 'class': 'test_class2'},
    ]

    elm = ElmFeatureProvider([])
    elm._full_motif_classes = full_classes

    eq_(expected, elm._get_more_info(test_inst))
