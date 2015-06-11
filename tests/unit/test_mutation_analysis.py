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

    from kmad_web.services.mutation_analysis import codon_to_features

    expected = {'ptm': {'type': 'phosphorylation', 'level': 4},
                'motif': 'aa'}
    result = codon_to_features(codon)

    eq_(result, expected)


def test_get_real_position():
    encoded_alignment = ['>seq1', 'AAAAAAA-AAAAAATAAAAAA-AAAAAA-AAAAAAZAAAAAA',
                         '>seq2', 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA']
    from kmad_web.services.mutation_analysis import get_real_position

    eq_(get_real_position(encoded_alignment, 1, 0), 2)
    eq_(get_real_position(encoded_alignment, 2, 0), 5)


def test_analyze_predictions():

    from kmad_web.services.mutation_analysis import analyze_predictions

    encoded_alignment = ['>seq1', 'SAAAAAASAAAAAASAAAAAASAAAAAA']
    pred_wild = [2, 3, 4]
    pred_mut = [2, 3]
    alignment = [[
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif':  ''
                      }
         },
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif':  ''
                      }
         },
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif': ''
                      }
         },
        {'aa': 'S',
         'features': {'ptm': {'type': 'phosphorylation', 'level': 0},
                      'motif': ''
                      }
         }
    ]]
    mutation_site = 0
    result = analyze_predictions(pred_wild, pred_mut, alignment, mutation_site,
                                 encoded_alignment)
    expected = [{'position': 4,
                 'ptm': {'phosphorylation': ['Y', 'N', 'description']}}]

    eq_(result, expected)


def test_analyze_ptms():

    from kmad_web.services.mutation_analysis import analyze_ptms

    alignment = [[
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif':  ''
                      }
         },
        {'aa': 'S',
         'features': {'ptm': {'type': 'phosphorylation', 'level': 0},
                      'motif': ''
                      }
         }
    ],
        [
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif':  ''
                      }
         },
        {'aa': 'S',
         'features': {'ptm': {'type': 'phosphorylation', 'level': 0},
                      'motif': ''
                      }
         }
    ]]
    mutation_site = 1
    alignment_position = 1
    new_aa = 'S'
    expected = {'position': 2,
                'ptms': {'phosphorylation': ['Y', 'Y', 'description']}}

    predicted_phosph_mutant = [1, 2]

    result = analyze_ptms(alignment, mutation_site, alignment_position, new_aa,
                          predicted_phosph_mutant)
    eq_(result, expected)

    new_aa = 'T'
    expected = {'position': 2,
                'ptms': {'phosphorylation': ['Y', 'N', 'description']}}
    result = analyze_ptms(alignment, mutation_site, alignment_position, new_aa,
                          predicted_phosph_mutant)
    eq_(result, expected)

    alignment = [[
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif':  ''
                      }
         },
        {'aa': 'S',
         'features': {'ptm': {'type': 'phosphorylation', 'level': 4},
                      'motif': ''
                      }
         }
    ],
        [
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif':  ''
                      }
         },
        {'aa': 'S',
         'features': {'ptm': {'type': 'phosphorylation', 'level': 0},
                      'motif': ''
                      }
         }
    ]]

    result = analyze_ptms(alignment, mutation_site, alignment_position, new_aa,
                          predicted_phosph_mutant)
    expected = {'position': 2,
                'ptms': {'phosphorylation': ['M', 'N', 'description']}}
    eq_(result, expected)

    alignment = [[
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif':  ''
                      }
         },
        {'aa': 'S',
         'features': {'ptm': {'type': 'hydroxylation', 'level': 3},
                      'motif': ''
                      }
         }
    ],
        [
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif':  ''
                      }
         },
        {'aa': 'S',
         'features': {'ptm': {'type': 'hydroxylation', 'level': 0},
                      'motif': ''
                      }
         }
    ]]
    result = analyze_ptms(alignment, mutation_site, alignment_position, new_aa,
                          predicted_phosph_mutant)
    expected = {'position': 2,
                'ptms': {'hydroxylation': ['Y', 'N', 'description']}}
    eq_(result, expected)


    alignment = [[
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif':  ''
                      }
         },
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif': ''
                      }
         }
    ],
        [
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif':  ''
                      }
         },
        {'aa': 'S',
         'features': {'ptm': {'type': 'hydroxylation', 'level': 0},
                      'motif': ''
                      }
         }
    ]]
    result = analyze_ptms(alignment, mutation_site, alignment_position, new_aa,
                          predicted_phosph_mutant)
    expected = {'position': 2,
                'ptms': {'hydroxylation': ['M', 'N', 'description']}}
    eq_(result, expected)

    alignment = [[
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif':  ''
                      }
         },
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif': ''
                      }
         }
    ],
        [
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif':  ''
                      }
         },
        {'aa': 'T',
         'features': {'ptm': {'type': 'phosphorylation', 'level': 0},
                      'motif': ''
                      }
         }
    ]]
    new_aa = 'T'
    predicted_phosph_mutant = [1]
    expected = {'position': 2,
                'ptms': {'phosphorylation': ['N', 'M', 'description']}}
    result = analyze_ptms(alignment, mutation_site, alignment_position, new_aa,
                          predicted_phosph_mutant)
    eq_(result, expected)


def test_analyze_motifs():
    alignment = [[
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif': 'ab'
                      }
         },
        {'aa': 'R',
         'features': {'ptm': {'type': 'phosphorylation', 'level': 0},
                      'motif': 'ab'
                      }
         }
    ],
        [
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif': 'aa'
                      }
         },
        {'aa': 'T',
         'features': {'ptm': {'type': 'phosphorylation', 'level': 0},
                      'motif': 'aa'
                      }
         }
    ],
        [
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif': 'aa'
                      }
         },
        {'aa': 'T',
         'features': {'ptm': {'type': 'phosphorylation', 'level': 0},
                      'motif': 'aa'
                      }
         }
    ],
        [
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif': 'ab'
                      }
         },
        {'aa': 'R',
         'features': {'ptm': {'type': 'phosphorylation', 'level': 0},
                      'motif': 'ab'
                      }
         }
    ]
    ]

    mutation_site = 1
    alignment_position = 1
    wild_seq = 'SR'
    mutant_seq = 'SK'
    proc_alignment = [['>1', 'SR'], ['>2', 'ST'],
                      ['>3', 'ST'], ['>4', 'SR']]
    annotated_motifs = [[[0, 2]], ['MOTIFC'], [1]]
    encoded_alignment = ['>1', 'SAAAAabRAAAAab', '>2', 'SAAAAaaTAAAAaa',
                         '>3', 'SAAAAaaTAAAAaa', '>4', 'SAAAAabRAAAAab']
    feature_codemap = {'motifs': [['aa', 'MOTIFA', 'ST'],
                                  ['ab', 'MOTIFB', 'SR'],
                                  ['ac', 'MOTIFC', 'S.']],
                       'domains': []}

    from kmad_web.services.mutation_analysis import analyze_motifs

    result = analyze_motifs(alignment, proc_alignment, encoded_alignment,
                            wild_seq, mutant_seq, mutation_site,
                            alignment_position, feature_codemap,
                            annotated_motifs)
    # motif A is not present in the first sequence
    expected = {'position': 2,
                'motifs': {'MOTIFB': ['M', 'N', 'description'],
                           'MOTIFC': ['Y', 'Y', 'description']}
                }

    eq_(result, expected)

    feature_codemap = {'motifs': [['aa', 'MOTIFA', 'ST'],
                                  ['ab', 'MOTIFB', 'SR'],
                                  ['ac', 'MOTIFC', 'SR']],
                       'domains': []}
    expected = {'position': 2,
                'motifs': {'MOTIFB': ['M', 'N', 'description'],
                           'MOTIFC': ['Y', 'N', 'description']}
                }
    result = analyze_motifs(alignment, proc_alignment, encoded_alignment,
                            wild_seq, mutant_seq, mutation_site,
                            alignment_position, feature_codemap,
                            annotated_motifs)
    eq_(result, expected)

    feature_codemap = {'motifs': [['aa', 'MOTIFA', 'ST'],
                                  ['ab', 'MOTIFB', 'S.'],
                                  ['ac', 'MOTIFC', 'SR']],
                       'domains': []}
    result = analyze_motifs(alignment, proc_alignment, encoded_alignment,
                            wild_seq, mutant_seq, mutation_site,
                            alignment_position, feature_codemap,
                            annotated_motifs)
    expected = {'position': 2,
                'motifs': {'MOTIFB': ['M', 'M', 'description'],
                           'MOTIFC': ['Y', 'N', 'description']}
                }


def test_get_motif_list():
    alignment = [[
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif': 'ab'
                      }
         },
        {'aa': 'R',
         'features': {'ptm': {'type': 'phosphorylation', 'level': 0},
                      'motif': 'ab'
                      }
         }
    ],
        [
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif': 'aa'
                      }
         },
        {'aa': 'T',
         'features': {'ptm': {'type': 'phosphorylation', 'level': 0},
                      'motif': 'aa'
                      }
         }
    ],
        [
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif': 'aa'
                      }
         },
        {'aa': 'T',
         'features': {'ptm': {'type': 'phosphorylation', 'level': 0},
                      'motif': 'aa'
                      }
         }
    ],
        [
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif': 'ab'
                      }
         },
        {'aa': 'R',
         'features': {'ptm': {'type': 'phosphorylation', 'level': 0},
                      'motif': 'ab'
                      }
         }
    ]
    ]
    wild_seq = 'SR'
    mutation_site = 1
    encoded_alignment = ['>1', 'SAAAAabRAAAAab', '>2', 'SAAAAaaTAAAAaa',
                         '>3', 'SAAAAaaTAAAAaa', '>4', 'SAAAAabRAAAAab']

    from kmad_web.services.mutation_analysis import get_motif_list

    result = get_motif_list(alignment, encoded_alignment, wild_seq,
                            mutation_site)

    eq_(result, set(['aa', 'ab']))


def test_process_annotated():
    annotated = [[[0, 1], [3, 4]], ['MOTIFA', 'MOTIFB'], [1, 1]]
    expected = {'aa': {'coords': [0, 1], 'name': 'MOTIFA', 'regex': 'ST'},
                'ab': {'coords': [3, 4], 'name': 'MOTIFB', 'regex': 'SR'}}
    feature_codemap = {'motifs': [['aa', 'MOTIFA', 'ST'],
                                  ['ab', 'MOTIFB', 'SR'],
                                  ['ac', 'MOTIFC', 'S.']],
                       'domains': []}

    from kmad_web.services.mutation_analysis import (process_annotated,
                                                     process_codemap)

    motif_dict = process_codemap(feature_codemap)

    eq_(process_annotated(annotated, motif_dict), expected)

