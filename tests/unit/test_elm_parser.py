from kmad_web.parsers.elm import ElmParser

from nose.tools import eq_


def test_parse_instances():
    with open('tests/unit/testdata/elm_instances.gff') as a:
        elm_result = a.read()
    elm = ElmParser()
    elm.parse_instances(elm_result)
    expected_motifs = [{'start': 137, 'end': 143, 'id': 'MOD_PIKK_1'}]
    eq_(expected_motifs, elm.motif_instances)


def test_parse_motif_classes():
    with open('tests/unit/testdata/test_elm_classes.tsv') as a:
            elm_data = a.read()
    elm_parser = ElmParser()
    elm_parser.parse_motif_classes(elm_data)
    expected = {'CLV_C14_Caspase3-7': {
        'description': 'Caspase-3 and Caspase-7 cleavage site.',
        'class': 'Caspase cleavage motif',
        'pattern': '[DSTE][^P][^DEWHFYC]D[GSAN]',
        'probability': '0.00309374033071'
        }
        }
    eq_(expected, elm_parser.motif_classes)
