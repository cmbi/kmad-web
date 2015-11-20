from nose.tools import eq_

from kmad_web.domain.mutation import Mutation
from kmad_web.domain.features.analysis.motifs import analyze_motifs


def test_analyze_motifs():
    sequences = [
        {
            'seq': 'SEQ',
            'ptms': [],
            'domains': [],
            'motifs': [
                {'id': 'm1', 'start': 1, 'end': 3, 'pattern': 'SE.',
                 'probability': 1, 'class': 'c1'},
                {'id': 'm3', 'start': 1, 'end': 3, 'pattern': 'S..',
                 'probability': 1, 'class': 'c3'},
                {'id': 'm4', 'start': 1, 'end': 3, 'pattern': '.E.',
                 'probability': 0.5, 'class': 'c4'}
            ],
            'aligned': 'SEQ'
        },
        {
            'seq': 'SEQ',
            'ptms': [],
            'domains': [],
            'motifs': [
                {'id': 'm1', 'start': 1, 'end': 3, 'pattern': 'SE.',
                 'probability': 1, 'class': 'c1'},
                {'id': 'm2', 'start': 1, 'end': 3, 'pattern': '.E.',
                 'probability': 1, 'class': 'c2'}
            ],
            'aligned': 'SEQ'
        },
        {
            'seq': 'SEQ',
            'ptms': [],
            'domains': [],
            'motifs': [
                {'id': 'm1', 'start': 1, 'end': 3, 'pattern': 'SE.',
                 'probability': 1, 'class': 'c1'},
                {'id': 'm2', 'start': 1, 'end': 3, 'pattern': '.E.',
                 'probability': 1, 'class': 'c2'}
            ],
            'aligned': 'SEQ'
        }
    ]

    new_aa = 'X'
    pos = 2
    m = Mutation(sequences[0], pos, new_aa)
    expected = {'position': 2,
                'motifs': {
                    'm1': {
                        'class': 'c1', 'wild': '4', 'mutant': '0',
                        'probability': 1},
                    'm3': {
                        'class': 'c3', 'wild': '4', 'mutant': '4',
                        'probability': 1}
                }}

    eq_(expected, analyze_motifs(m, sequences))
