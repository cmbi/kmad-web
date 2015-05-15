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
                          'code': 'aa',
                          'name': 'SOMEMOTIF'}}
    result = codon_to_features(codon, feature_codemap)

    eq_(result, expected)


def test_get_real_position():
    encoded_alignment = ['>seq1', 'AAAAAAA-AAAAAATAAAAAA-AAAAAA-AAAAAAZAAAAAA',
                         '>seq2', 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA']
    from kmad_web.services.mutation_analysis import get_real_position

    eq_(get_real_position(encoded_alignment, 1, 0), 2)
    eq_(get_real_position(encoded_alignment, 2, 0), 5)


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
                 'ptms': {'phosphorylation': ['certain', 'N',
                                              'description']}}]
    # expected = [{'position': 3,
    #              'ptms': [{'type': 'phosphorylation',
    #                        'level': 0,
    #                        'status_wild': 'certain',
    #                        'status_mut': 'N'
    #                        }]
    #              },
    #             ]

    eq_(result, expected)


def test_analyze_ptms():

    from kmad_web.services.mutation_analysis import analyze_ptms

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
    ],
        [
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif':  {}
                      }
         },
        {'aa': 'S',
         'features': {'ptm': {'type': 'phosphorylation', 'level': 0},
                      'motif': {}
                      }
         }
    ]]
    mutation_site = 1
    alignment_position = 1
    new_aa = 'S'
    expected = {'position': 1,
                'ptms': {'phosphorylation': ['certain', 'Y', 'description']}}
    # expected = [{'position': 1,
    #              'ptms': [{'type': 'phosphorylation',
    #                        'level': 0,
    #                        'status_wild': 'certain',
    #                        'status_mut': 'Y',
    #                        'description': ''
    #                        }]
    #              }]
    result = analyze_ptms(alignment, mutation_site, alignment_position, new_aa)
    eq_(result, expected)

    new_aa = 'T'
    expected = {'position': 1,
                'ptms': {'phosphorylation': ['certain', 'N', 'description']}}
    # expected = [{'position': 1,
    #              'ptms': [{'type': 'phosphorylation',
    #                        'level': 0,
    #                        'status_wild': 'certain',
    #                        'status_mut': 'N',
    #                        'description': ''
    #                        }]
    #              }]
    result = analyze_ptms(alignment, mutation_site, alignment_position, new_aa)
    eq_(result, expected)


def test_analyze_motifs():
    alignment = [[
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif': {
                          'code': 'ab',
                          'name': 'ab',
                          'regex': 'SR'}
                      }
         },
        {'aa': 'R',
         'features': {'ptm': {'type': 'phosphorylation', 'level': 0},
                      'motif': {
                          'code': 'ab',
                          'name': 'ab',
                          'regex': 'SR'}
                      }
         }
    ],
        [
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif':  {
                          'code': 'aa',
                          'name': 'aa',
                          'regex': 'ST'}
                      }
         },
        {'aa': 'T',
         'features': {'ptm': {'type': 'phosphorylation', 'level': 0},
                      'motif': {
                          'code': 'aa',
                          'name': 'aa',
                          'regex': 'ST'}
                      }
         }
    ],
        [
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif':  {
                          'code': 'aa',
                          'name': 'aa',
                          'regex': 'ST'}
                      }
         },
        {'aa': 'T',
         'features': {'ptm': {'type': 'phosphorylation', 'level': 0},
                      'motif': {
                          'code': 'aa',
                          'name': 'aa',
                          'regex': 'ST'}
                      }
         }
    ],
        [
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif': {
                          'code': 'ab',
                          'name': 'ab',
                          'regex': 'SR'}
                      }
         },
        {'aa': 'R',
         'features': {'ptm': {'type': 'phosphorylation', 'level': 0},
                      'motif': {
                          'code': 'ab',
                          'name': 'ab',
                          'regex': 'SR'}
                      }
         }
    ]
    ]

    mutation_site = 1
    alignment_position = 1
    wild_seq = 'SR'
    mutant_seq = 'SK'
    raw_alignment = [['>1', 'SR'], ['>2', 'ST'],
                     ['>3', 'ST'], ['>4', 'SR']]
    encoded_alignment = ['>1', 'SAAAAabRAAAAab', '>2', 'SAAAAaaTAAAAaa',
                         '>3', 'SAAAAaaTAAAAaa', '>4', 'SAAAAabRAAAAab']
    feature_codemap = {'motifs': [['aa', 'SOMEMOTIF', 'ST'],
                                  ['ab', 'SOMEOTHERMOTIF', 'SR']],
                       'domains': []}

    from kmad_web.services.mutation_analysis import analyze_motifs

    result = analyze_motifs(alignment, raw_alignment, encoded_alignment,
                            wild_seq, mutant_seq, mutation_site,
                            alignment_position, feature_codemap)

    expected = [{'MOTIFB': ['putative', 'N', 'description']}]
    # eq_(result, expected)


def test_get_motif_list():
    alignment = [[
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif': {
                          'code': 'ab',
                          'name': 'ab',
                          'regex': 'SR'}
                      }
         },
        {'aa': 'R',
         'features': {'ptm': {'type': 'phosphorylation', 'level': 0},
                      'motif': {
                          'code': 'ab',
                          'name': 'ab',
                          'regex': 'SR'}
                      }
         }
    ],
        [
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif':  {
                          'code': 'aa',
                          'name': 'aa',
                          'regex': 'ST'}
                      }
         },
        {'aa': 'T',
         'features': {'ptm': {'type': 'phosphorylation', 'level': 0},
                      'motif': {
                          'code': 'aa',
                          'name': 'aa',
                          'regex': 'ST'}
                      }
         }
    ],
        [
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif':  {
                          'code': 'aa',
                          'name': 'aa',
                          'regex': 'ST'}
                      }
         },
        {'aa': 'T',
         'features': {'ptm': {'type': 'phosphorylation', 'level': 0},
                      'motif': {
                          'code': 'aa',
                          'name': 'aa',
                          'regex': 'ST'}
                      }
         }
    ],
        [
        {'aa': 'S',
         'features': {'ptm': {},
                      'motif': {
                          'code': 'ab',
                          'name': 'ab',
                          'regex': 'SR'}
                      }
         },
        {'aa': 'R',
         'features': {'ptm': {'type': 'phosphorylation', 'level': 0},
                      'motif': {
                          'code': 'ab',
                          'name': 'ab',
                          'regex': 'SR'}
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
