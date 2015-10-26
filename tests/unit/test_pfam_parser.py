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
        set([i['accession'] for i in pfam._domains]))
    # check single domain with one occurence
    pfam = PfamParser()
    with open('tests/unit/testdata/crambin_pfam.xml') as a:
        pfam_result = a.read()

    pfam.parse(pfam_result)
    expected_accession = 'PF00321.13'
    eq_(1, len(pfam._domains))
    eq_(expected_accession, pfam._domains[0]['accession'])
