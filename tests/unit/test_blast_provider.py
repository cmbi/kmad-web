from mock import patch, MagicMock, PropertyMock
from nose.tools import eq_, ok_

from kmad_web.domain.blast.provider import BlastResultProvider


@patch('kmad_web.services.blast.subprocess.check_output')
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
    eq_(blast_hits, blast.get_result(fasta_file))


def test_get_exact_hit():
    test_id = 'test_id'
    test_hits = [{'slen': 1, 'qlen': 3, 'pident': '100.00', 'id': test_id}]

    blast = BlastResultProvider('test_path')
    ok_(not blast.get_exact_hit(test_hits))

    test_hits = [{'slen': 3, 'qlen': 3, 'pident': '100.00', 'id': test_id}]

    eq_(test_id, blast.get_exact_hit(test_hits))
