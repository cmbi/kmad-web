from kmad_web.parsers.elm import ElmParser

from nose.tools import eq_


def test_parse():
    with open('tests/unit/testdata/elm_instances.gff') as a:
        elm_result = a.read()
    elm = ElmParser()
    elm.parse(elm_result)
    expected_motifs = [{'start': 137, 'end': 143, 'id': 'MOD_PIKK_1'}]
    eq_(expected_motifs, elm._motifs)
