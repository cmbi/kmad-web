from nose.tools import eq_, ok_, with_setup
from mock import patch

from kmad_web.domain.mutation import Mutation
from kmad_web.domain.features.analysis.ptms import (analyze_ptms,
                                                    _analyze_predicted_phosph,
                                                    _analyze_annotated_ptms,
                                                    _check_local_similarity,
                                                    _get_all_names)
from kmad_web.domain.features.analysis.helpers import (
    group_features_positionwise)
from kmad_web.services.helpers.cache import cache_manager as cm


def setup():
    cm.load_config({
        'redis': {'redis.backend': 'dogpile.cache.null'}
    })


def teardown():
    cm.reset()


@with_setup(setup, teardown)
@patch('kmad_web.domain.features.providers.netphos.NetphosFeatureProvider.get_phosphorylations')
def test_analyze_ptms(mock_netphos):
    mock_netphos.return_value = []
    sequences = [
        {
            'seq': 'ABC',
            'ptms': [
                {'name': 'phosphorylation', 'position': 2,
                 'annotation_level': 2, 'info': ""},
                {'name': 'phosphorylation', 'position': 3,
                 'annotation_level': 2, 'info': ""}
            ],
            'motifs': [],
            'domains': [],
            'aligned': 'ABC'
        },
        {
            'seq': 'ABC',
            'ptms': [
                {'name': 'phosphorylation', 'position': 2,
                 'annotation_level': 2, 'info': ""},
                {'name': 'amidation', 'position': 2,
                 'annotation_level': 2, 'info': ""}
            ],
            'motifs': [],
            'domains': [],
            'aligned': 'ABC'
        },
        {
            'seq': 'ABC',
            'ptms': [
                {'name': 'phosphorylation', 'position': 2,
                 'annotation_level': 2, 'info': ""},
                {'name': 'amidation', 'position': 2,
                 'annotation_level': 2, 'info': ""}
            ],
            'motifs': [],
            'domains': [],
            'aligned': 'ABC'
        },
        {
            'seq': 'AXC',
            'ptms': [
                {'name': 'amidation', 'position': 2,
                 'annotation_level': 2, 'info': ""}
            ],
            'motifs': [],
            'domains': [],
            'aligned': 'AXC'
        }
    ]
    new_aa = 'X'
    pos = 2
    m = Mutation(sequences[0], pos, new_aa)
    expected = {
        'residues': [
            {'position': 2,
             'ptms': {
                 'amidation': {'wild': '3', 'mutant': '3', 'info': ""},
                 'phosphorylation': {'wild': '4', 'mutant': '0', 'info': ""}
             }}]}
    eq_(expected, analyze_ptms(m, sequences))


def test_analyze_predicted_phosph():
    sequences = [
        {
            'seq': 'SSS',
            'ptms': [
                {'name': 'phosphorylation', 'position': 2,
                 'annotation_level': 2, 'info': ""},
                {'name': 'phosphorylation', 'position': 3,
                 'annotation_level': 2, 'info': ""}
            ],
            'motifs': [],
            'domains': [],
            'aligned': 'SSS'
        },
        {
            'seq': 'CCC',
            'aligned': 'CCC',
            'ptms': [],
            'motifs': [],
            'domains': []
        },
        {
            'seq': 'CCC',
            'aligned': 'CCC',
            'ptms': [],
            'motifs': [],
            'domains': []
        }
    ]
    new_aa = 'X'
    pos = 3
    m = Mutation(sequences[0], pos, new_aa)
    group_features_positionwise(sequences)
    missing = [0, 1]
    expected = [
        {'position': 2,
         'ptms': {
             'phosphorylation': {'wild': '4', 'mutant': '0', 'info': ""}
         }}
    ]
    eq_(expected, _analyze_predicted_phosph(m, sequences, missing))


def test_check_local_similarity():
    new_aa = 'X'
    pos = 3
    sequences = [
        {'seq': 'SSSSSS', 'aligned': 'SSS---SSS'},
        {'seq': 'SSSSSS', 'aligned': 'SSS---SSS'}
    ]
    m = Mutation(sequences[0], pos, new_aa)
    seq1 = 'SSS---SSS'
    seq2 = 'SSS---SSS'
    ok_(_check_local_similarity(m, seq1, seq2))

    pos = 6
    m = Mutation(sequences[0], pos, new_aa)
    ok_(_check_local_similarity(m, seq1, seq2))


def test_analyze_annotated_ptms():
    sequences = [
        {
            'seq': 'ABC',
            'ptms': [],
            'motifs': [],
            'domains': [],
            'aligned': 'ABC'
        },
        {
            'seq': 'ABC',
            'ptms': [
                {'name': 'amidation', 'position': 2,
                 'annotation_level': 2}
            ],
            'motifs': [],
            'domains': [],
            'aligned': 'ABC'
        },
        {
            'seq': 'ABC',
            'ptms': [
                {'name': 'amidation', 'position': 2,
                 'annotation_level': 2}
            ],
            'motifs': [],
            'domains': [],
            'aligned': 'ABC'
        },
        {
            'seq': 'AXC',
            'ptms': [
                {'name': 'amidation', 'position': 2,
                 'annotation_level': 2}
            ],
            'motifs': [],
            'domains': [],
            'aligned': 'AXC'
        },
        {
            'seq': 'AXC',
            'ptms': [
                {'name': 'amidation', 'position': 2,
                 'annotation_level': 2}
            ],
            'motifs': [],
            'domains': [],
            'aligned': 'AXC'
        }
    ]

    pos = 2
    new_aa = 'X'
    ptm_names = _get_all_names(sequences)
    m = Mutation(sequences[0], pos, new_aa)
    group_features_positionwise(sequences)
    expected = {'position': 2, 'ptms': {'amidation':
                                        {'wild': '3', 'mutant': '3', 'info': ""}}}
    eq_(expected, _analyze_annotated_ptms(m, sequences, [], [], ptm_names))

    sequences = [
        {
            'seq': 'ABC',
            'ptms': [],
            'motifs': [],
            'domains': [],
            'aligned': 'ABC'
        },
        {
            'seq': 'ABC',
            'ptms': [],
            'motifs': [],
            'domains': [],
            'aligned': 'ABC'
        },
        {
            'seq': 'ABC',
            'ptms': [
                {'name': 'amidation', 'position': 2,
                 'annotation_level': 2}
            ],
            'motifs': [],
            'domains': [],
            'aligned': 'ABC'
        },
        {
            'seq': 'AXC',
            'ptms': [
                {'name': 'amidation', 'position': 2,
                 'annotation_level': 2}
            ],
            'motifs': [],
            'domains': [],
            'aligned': 'AXC'
        },
        {
            'seq': 'AXC',
            'ptms': [
                {'name': 'amidation', 'position': 2,
                 'annotation_level': 2}
            ],
            'motifs': [],
            'domains': [],
            'aligned': 'AXC'
        }
    ]

    pos = 2
    new_aa = 'A'
    m = Mutation(sequences[0], pos, new_aa)
    group_features_positionwise(sequences)
    ptm_names = _get_all_names(sequences)
    expected = {'position': 2, 'ptms': {'amidation':
                                        {'wild': '3', 'mutant': '0', 'info': ""}}}
    eq_(expected, _analyze_annotated_ptms(m, sequences, [], [], ptm_names))

    sequences = [
        {
            'seq': 'ABC',
            'ptms': [],
            'motifs': [],
            'domains': [],
            'aligned': 'ABC'
        },
        {
            'seq': 'ABC',
            'ptms': [],
            'motifs': [],
            'domains': [],
            'aligned': 'ABC'
        },
        {
            'seq': 'ABC',
            'ptms': [
                {'name': 'amidation', 'position': 2,
                 'annotation_level': 2, 'info': ""}
            ],
            'motifs': [],
            'domains': [],
            'aligned': 'ABC'
        },
        {
            'seq': 'AXC',
            'ptms': [
                {'name': 'amidation', 'position': 2,
                 'annotation_level': 2, 'info': ""}
            ],
            'motifs': [],
            'domains': [],
            'aligned': 'AXC'
        }
    ]

    pos = 2
    new_aa = 'X'
    m = Mutation(sequences[0], pos, new_aa)
    ptm_names = _get_all_names(sequences)
    group_features_positionwise(sequences)
    expected = {'position': 2, 'ptms': {'amidation':
                                        {'wild': '2', 'mutant': '2', 'info': ""}}}
    eq_(expected, _analyze_annotated_ptms(m, sequences, [], [], ptm_names))
