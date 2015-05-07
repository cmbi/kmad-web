from nose.tools import eq_


def test_create_mutant_sequence():

    from kmad_web.services.mutation_analysis import create_mutant_sequence

    seq = "SEQ"
    mutation_site = 1
    new_aa = "P"
    result = create_mutant_sequence(seq, mutation_site, new_aa)
    expected = "SPQ"
    eq_(expected, result)


def test_codon_to_features():
    codon = 'AAAAdaa'
    feature_codemap = {'motifs': [['aa', 'SOMEMOTIF', 'SOMEREGEX']],
                       'domains': []}

    from kmad_web.services.mutation_analysis import codon_to_features

    expected = {'ptm': {'type': 'phosphorylation', 'level': 4},
                'motif': {'regex': 'SOMEREGEX',
                          'name': 'SOMEMOTIF'}}
    result = codon_to_features(codon, feature_codemap)

    eq_(result, expected)


def test_get_real_position():
    encoded_alignment = ['>seq1', 'AAAAAAA-AAAAAATAAAAAA-AAAAAA-AAAAAAZAAAAAA',
                         '>seq2', 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA']
    from kmad_web.services.mutation_analysis import get_real_position

    eq_(get_real_position(encoded_alignment, 1), 2)
    eq_(get_real_position(encoded_alignment, 2), 5)


def test_analyze_predictions():

    from kmad_web.services.mutation_analysis import analyze_predictions

    encoded_alignment = ['>seq1', 'SAAAAAASAAAAAASAAAAAASAAA']
    pred_wild = [1, 2, 3]
    pred_mut = [1, 2]
    alignment = [[
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif':  {}
                      }
         },
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif':  {}
                      }
         },
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif':  {}
                      }
         },
        {'aa': 'S',
         'features': {'ptm': {'type': 'phosphorylation', 'level': 0},
                      'motif':  {}
                      }
         }
    ]]
    mutation_site = 0
    result = analyze_predictions(pred_wild, pred_mut, alignment, mutation_site,
                                 encoded_alignment)

    expected = [{'position': 3,
                 'ptms': [{'type': 'phosphorylation',
                           'level': 0,
                           'status_wild': 'certain',
                           'status_mut': 'N'
                           }]
                 },
                ]

    eq_(result, expected)


def test_analyze_ptms(alignment, mutation_site, alignment_position, new_aa):
    alignment = [[
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif':  {}
                      }
         },
        {'aa': 'S',
         'features': {'ptm': {'type': 'phosphorylation', 'level': 0},
                      'motif':  {}
                      }
         }
    ]
        [
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif':  {}
                      }
         },
        {'aa': 'S',
         'features': {'ptm': {'type': 'phosphorylation', 'level': 0},
                      'motif':  {}
                      }
         }
    ]]
    mutation_site = 1
    alignment_position = 1
    new_aa = 'T'

