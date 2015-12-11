from mock import patch, PropertyMock
from nose.tools import eq_, ok_, with_setup

from kmad_web.domain.blast.provider import BlastResultProvider
from kmad_web.services.helpers.cache import cache_manager as cm


def setup():
    cm.load_config({
        'redis': {'redis.backend': 'dogpile.cache.null'}
    })


def teardown():
    cm.reset()


@patch('kmad_web.services.blast.subprocess.check_output')
@with_setup(setup, teardown)
def test_get_result(mock_check_output):
    fasta_file = ">1\nSEQSEQSEQ\n"
    blast_result = "test,sp|P01542|CRAM_CRAAB,100.00," \
                   "0,1e-25,93.2,46,50"

    mock_check_output.return_value = blast_result
    blast = BlastResultProvider('test_path')
    blast_hits = [
        {
            'pident': '100.00',
            'slen': '46',
            'qlen': '50',
            'evalue': '1e-25',
            'mismatch': '0',
            'entry_name': 'CRAM_CRAAB',
            'id': 'P01542',
            'header': 'sp|P01542|CRAM_CRAAB',
            'bitscore': '93.2'
        }
    ]
    eq_(blast_hits, blast.get_result(fasta_file, 1000))


def test_get_exact_hit():
    test_id = 'test_id'
    test_hits = [{'slen': 1, 'qlen': 3, 'pident': '100.00', 'id': test_id}]

    blast = BlastResultProvider('test_path')
    ok_(not blast.get_exact_hit(test_hits))

    test_hits = [{'slen': 3, 'qlen': 3, 'pident': '100.00', 'id': test_id}]

    eq_(test_id, blast.get_exact_hit(test_hits))
