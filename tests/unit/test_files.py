import os
from mock import patch
from nose.tools import eq_, ok_

from testdata import test_variables as test_vars


@patch('kman_web.services.files.get_seq_from_uniprot')
@patch('kman_web.services.files.open', create=True)
def test_get_fasta_from_blast(mock_open, test_get_seq):
    m_file = mock_open.return_value.__enter__.return_value
    test_blast = open('tests/unit/testdata/test.blastp').read()
    test_get_seq.side_effect = lambda x: seq_calls.pop(0)

    # check: query sequence the same as the first blast hit
    reads = ['>testseq1\nSEQ\n', test_blast]
    m_file.read.side_effect = lambda: reads.pop(0)
    seq_calls = [['>testseq1\n', 'SEQ'], ['>testseq2\n', 'SE']]
    expected_data = '>testseq1\nSEQ\n>testseq2\nSE\n'

    from kman_web.services.files import get_fasta_from_blast

    get_fasta_from_blast('blastname', 'fastaname')
    handle = mock_open()
    handle.write.assert_called_once_with(expected_data)

    # check: query sequence different than teh first blast hit
    reads = ['>testseq0\nSEQSEQ\n', test_blast]
    seq_calls = [['>testseq1\n', 'SEQ'], ['>testseq2\n', 'SE']]
    expected_data = '>testseq0\nSEQSEQ\n>testseq1\nSEQ\n>testseq2\nSE\n'
    handle.reset_mock()

    get_fasta_from_blast('blastname', 'fastaname')
    handle.write.assert_called_once_with(expected_data)


def test_is_empty():
    from kman_web.services.files import is_empty

    ok_(is_empty(' '))
    ok_(not is_empty('abc'))


def test_get_seq_from_uniprot():
    from kman_web.services.files import get_seq_from_uniprot

    expected = test_vars.ins_human_seq
    result = get_seq_from_uniprot('INS_HUMAN')
    eq_(expected, result)


def test_write_single_fasta():
    from kman_web.services.files import write_single_fasta

    expected = '>1\nSEQ\nSEQ'
    fasta_input = '>1\nSEQ\nSEQ\n>2\nSEQSEQ\n>3\nSEQ\n'
    outname = write_single_fasta(fasta_input)
    with open(outname) as a:
        outfile = a.read()
    eq_(expected, outfile)
    os.remove(outname)
