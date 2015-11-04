from nose.tools import eq_

from kmad_web.domain.features.providers.elm import ElmFeatureProvider


def test_filter_motifs():
    test_motifs = [{'start': 1, 'end': 5, 'probability': 0.5},
                   {'start': 2, 'end': 4, 'probability': 0.5},
                   {'start': 5, 'end': 8, 'probability': 0.8}
                   ]
    expected_motifs = [{'start': 2, 'end': 4, 'probability': 0.5},
                       {'start': 5, 'end': 8, 'probability': 0.8}]
    elm = ElmFeatureProvider('test_path')
    eq_(expected_motifs, elm.filter_motifs(test_motifs))
