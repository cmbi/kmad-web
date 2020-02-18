from nose.tools import eq_, ok_
from kmad_web.parsers.uniprot import UniprotParser, valid_uniprot_id


def test_parse_txt():
    with open("tests/unit/testdata/test.txt") as a:
        test_txt = a.read()
    uniprot = UniprotParser()
    uniprot.parse_ptms(test_txt)
    exp_ptms = {'info': 'Phosphoserine',
                'position': '515',
                'eco': ['0000269'],
                'type': 'MOD_RES',
                'pub_med': set(['16923168'])
                }
    eq_(uniprot.ptms[0], exp_ptms)
    exp_go_term = {'source': 'IDA:UniProtKB',
                   'code': '0030424',
                   'type': 'C',
                   'description': 'axon'}
    uniprot.parse_go_terms(test_txt)
    eq_(uniprot.go_terms[0], exp_go_term)


def test_parse_ptms():
    with open("tests/unit/testdata/P21815.txt") as a:
        test_txt = a.read()
    uniprot = UniprotParser()
    uniprot.parse_ptms(test_txt)
    print(uniprot.ptms)


def test_parse_structure():
    with open("tests/unit/testdata/Q8CFN5.txt") as a:
        test_txt = a.read()
    uniprot = UniprotParser()
    uniprot.parse_structure(test_txt)

    expected = [
        {'start': 22, 'end': 38, 'name': 'HELIX'},
        {'start': 42, 'end': 48, 'name': 'STRAND'},
        {'start': 54, 'end': 60, 'name': 'STRAND'},
        {'start': 62, 'end': 70, 'name': 'HELIX'},
        {'start': 77, 'end': 79, 'name': 'STRAND'},
        {'start': 81, 'end': 88, 'name': 'HELIX'}
    ]

    eq_(uniprot.structure, expected)


def test_valid_uniprot_id():
    ok_(not valid_uniprot_id('seq'))
    ok_(valid_uniprot_id('P01542'))
    ok_(valid_uniprot_id('CRAM_CRAAB'))
