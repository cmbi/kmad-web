from nose.tools import eq_
from kmad_web.parsers.pfam import PfamParser

def test_parse():
    # check multiple domains with multiple occurences
    pfam = PfamParser()
    with open('tests/unit/testdata/hybrid_pfam.xml') as a:
        pfam_result = a.read()

    pfam.parse(pfam_result)
    eq_(5, len(pfam._domains))
    eq_(set(['PF00321.13', 'PF00418.15']),
        set([i['acc'] for i in pfam._domains]))
    # check single domain with one occurence
    pfam = PfamParser()
    with open('tests/unit/testdata/crambin_pfam.xml') as a:
        pfam_result = a.read()

    pfam.parse(pfam_result)
    expected = [{
        'acc': 'PF00321.13',
        'start': '1',
        'end': '46'
        }]
    eq_(expected, pfam._domains)

