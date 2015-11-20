from nose.tools import eq_, assert_raises
from kmad_web.domain.features.analysis.helpers import (
    get_seq_position, get_seq_range, group_features_positionwise)


def test_get_seq_range():
    seq = "A---A"
    aln_start = 1
    aln_end = 5
    expected = {
        'start': 1,
        'end': 2
    }
    eq_(expected, get_seq_range(seq, aln_start, aln_end))
    seq = "AA--A"
    expected = {
        'start': 1,
        'end': 3
    }
    eq_(expected, get_seq_range(seq, aln_start, aln_end))

    seq = "A--------A"
    expected = {
        'start': None,
        'end': None
    }
    eq_(expected, get_seq_range(seq, aln_start, aln_end))

    seq = "SEQ"
    aln_start = 0
    aln_end = 3
    expected = {
        'start': 0,
        'end': 3
    }
    eq_(expected, get_seq_range(seq, aln_start, aln_end))


def test_get_seq_position():
    seq = "A---A-"
    pos = 1
    assert_raises(AssertionError, get_seq_position, seq, pos)

    seq = "A---A-"
    pos = 4
    eq_(1, get_seq_position(seq, pos))


def test_group_features_positionwise():
    sequences = [
        {
            'seq': 'ABC',
            'ptms': [
                {'name': 'ptm1', 'position': 2},
                {'name': 'ptm2', 'position': 3}
            ],
            'motifs': [
                {'id': 'm1', 'start': 1, 'end': 2},
                {'id': 'm2', 'start': 1, 'end': 2}
            ],
            'domains': [
                {'accession': 'd1', 'start': 2, 'end': 2}
            ]
        }
    ]

    expected = [
        {'domains': [],
         'ptms': [],
         'motifs': [
             {'start': 1, 'end': 2, 'id': 'm1'},
             {'start': 1, 'end': 2, 'id': 'm2'}
        ]},
        {'domains': [{'start': 2, 'end': 2, 'accession': 'd1'}],
         'ptms': [{'position': 2, 'name': 'ptm1'}],
         'motifs': [
             {'start': 1, 'end': 2, 'id': 'm1'},
             {'start': 1, 'end': 2, 'id': 'm2'}
        ]},
        {'domains': [],
         'ptms': [{'position': 3, 'name': 'ptm2'}],
         'motifs': []
         }
    ]

    group_features_positionwise(sequences)
    eq_(expected, sequences[0]['feat_pos'])
