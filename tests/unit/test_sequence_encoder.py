from nose.tools import eq_

from kmad_web.domain.sequences.encoder import SequencesEncoder


def test_encode():
    test_sequences = [
        {
            'header': 'seq1',
            'seq': 'SEQ',
            'ptms': [
                {'name': 'phosphorylation', 'position': 1,
                 'annotation_level': 1},
                {'name': 'methylation', 'position': 1,
                 'annotation_level': 0},
                {'name': 'phosphorylation', 'position': 2,
                 'annotation_level': 0},
                {'name': 'methylation', 'position': 2,
                 'annotation_level': 0},
            ],
            'motifs': [
                {'id': 'test_motif',
                 'start': 1,
                 'end': 3}
            ],
            'domains': [
                {'accession': 'test_domain_1', 'start': 1, 'end': 1},
                {'accession': 'test_domain_2', 'start': 2, 'end': 3},
            ]
        }
    ]

    encoder = SequencesEncoder()
    encoder.encode(test_sequences)
    eq_("SA01V00EA00N00QA00A00", test_sequences[0]['encoded_seq'])
