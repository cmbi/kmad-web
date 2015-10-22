from nose.tools import eq_
from kmad_web.parsers.uniprot import UniprotParser


def test_parse_txt():
    with open("tests/unit/testdata/test.txt") as a:
        test_txt = a.read()
    uniprot = UniprotParser()
    uniprot.parse_txt(test_txt)
    exp_feat = {'info': 'Phosphoserine; by PDPK1 and TTBK1.',
                'position': '515',
                'eco': ['0000269'],
                'type': 'MOD_RES',
                'pub_med': set(['16923168'])
                }
    exp_go_term = {'source': 'IDA:UniProtKB',
                   'code': '0030424',
                   'type': 'C',
                   'description': 'axon'}
    eq_(uniprot._features[0], exp_feat)
    eq_(uniprot._go_terms[0], exp_go_term)
