from nose.tools import eq_, assert_raises, ok_
from kmad_web.domain.mutation import Mutation


def test_get_seq_range():
    m = Mutation('SEQ', 1, 'A')
    seq = "A---A"
    aln_start = 1
    aln_end = 5
    expected = {
        'start': 1,
        'end': 2
    }
    eq_(expected, m._get_seq_range(seq, aln_start, aln_end))
    seq = "AA--A"
    expected = {
        'start': 1,
        'end': 3
    }
    eq_(expected, m._get_seq_range(seq, aln_start, aln_end))

    seq = "A--------A"
    expected = {
        'start': None,
        'end': None
    }
    eq_(expected, m._get_seq_range(seq, aln_start, aln_end))

    seq = "SEQ"
    aln_start = 0
    aln_end = 3
    expected = {
        'start': 0,
        'end': 3
    }
    eq_(expected, m._get_seq_range(seq, aln_start, aln_end))


def test_get_seq_position():
    m = Mutation('SEQ', 1, 'A')
    seq = "A---A-"
    pos = 1
    assert_raises(AssertionError, m._get_seq_position, seq, pos)

    seq = "A---A-"
    pos = 4
    eq_(1, m._get_seq_position(seq, pos))


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

    m = Mutation('SEQ', 1, 'A')
    m._group_features_positionwise(sequences)
    eq_(expected, sequences[0]['feat_pos'])


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
    m = Mutation('SEQ', pos, new_aa)
    expected = {'position': 2,
                'motifs': {
                    'm1': {
                        'class': 'c1', 'wild': '4', 'mutant': '0',
                        'probability': 1},
                    'm3': {
                        'class': 'c3', 'wild': '4', 'mutant': '4',
                        'probability': 1}
                }}
    eq_(expected, m.analyze_motifs(sequences))


def test_analyze_ptms():
    sequences = [
        {
            'seq': 'ABC',
            'ptms': [
                {'name': 'phosphorylation', 'position': 2,
                 'annotation_level': 2},
                {'name': 'phosphorylation', 'position': 3,
                 'annotation_level': 2}
            ],
            'motifs': [],
            'domains': [],
            'aligned': 'ABC'
        },
        {
            'seq': 'ABC',
            'ptms': [
                {'name': 'phosphorylation', 'position': 2,
                 'annotation_level': 2},
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
                {'name': 'phosphorylation', 'position': 2,
                 'annotation_level': 2},
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
        }
    ]
    new_aa = 'X'
    pos = 2
    m = Mutation('ABC', pos, new_aa)
    expected = {
        'residues': [
            {'position': 2,
             'ptms': {
                 'amidation': {'wild': '3', 'mutant': '3'},
                 'phosphorylation': {'wild': '4', 'mutant': '0'}
             }}]}
    eq_(expected, m.analyze_ptms(sequences))


def test_analyze_predicted_phosph():
    sequences = [
        {
            'seq': 'SSS',
            'ptms': [
                {'name': 'phosphorylation', 'position': 2,
                 'annotation_level': 2},
                {'name': 'phosphorylation', 'position': 3,
                 'annotation_level': 2}
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
    m = Mutation('SSS', pos, new_aa)
    m._group_features_positionwise(sequences)
    missing = [0, 1]
    expected = [
        {'position': 2,
         'ptms': {
             'phosphorylation': {'wild': '4', 'mutant': '0'}
         }}
    ]
    eq_(expected, m._analyze_predicted_phosph(sequences, missing))


def test_check_local_similarity():
    new_aa = 'X'
    pos = 3
    m = Mutation('SSSSSS', pos, new_aa)
    m._alignment_position = 0
    seq1 = 'SSS---SSS'
    seq2 = 'SSS---SSS'
    ok_(m._check_local_similarity(seq1, seq2))

    pos = 6
    m = Mutation('SSSSSS', pos, new_aa)
    m._alignment_position = 8
    ok_(m._check_local_similarity(seq1, seq2))


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
    m = Mutation('ABC', pos, new_aa)
    m._alignment_position = 1
    m._group_features_positionwise(sequences)
    expected = {'position': 2, 'ptms': {'amidation':
                                        {'wild': '3', 'mutant': '3'}}}
    eq_(expected, m._analyze_annotated_ptms(sequences, [], []))

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
    m = Mutation('ABC', pos, new_aa)
    m._alignment_position = 1
    m._group_features_positionwise(sequences)
    expected = {'position': 2, 'ptms': {'amidation':
                                        {'wild': '3', 'mutant': '0'}}}
    eq_(expected, m._analyze_annotated_ptms(sequences, [], []))

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
        }
    ]

    pos = 2
    new_aa = 'X'
    m = Mutation('ABC', pos, new_aa)
    m._group_features_positionwise(sequences)
    m._alignment_position = 1
    expected = {'position': 2, 'ptms': {'amidation':
                                        {'wild': '2', 'mutant': '2'}}}
    eq_(expected, m._analyze_annotated_ptms(sequences, [], []))
