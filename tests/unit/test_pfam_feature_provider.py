from nose.tools import eq_

from kmad_web.domain.features.providers.pfam import PfamFeatureProvider


def test_get_domains():
    pfam_provider = PfamFeatureProvider()

    with open('tests/unit/testdata/TAU_HUMAN.fasta') as a:
        tau_fasta = a.read().splitlines()
    expected = ['PF00418.15'] * 4
    seq = ''.join(tau_fasta[1:])
    result = pfam_provider.get_domains({'seq': seq})
    eq_(expected, [d['accession'] for d in result])

    with open('tests/unit/testdata/CRAM_CRAAB.fasta') as a:
        cram_fasta = a.read().splitlines()

    expected = ['PF00321.13']
    seq = ''.join(cram_fasta[1:])
    result = pfam_provider.get_domains({'seq': seq})
    eq_(expected, [d['accession'] for d in result])
