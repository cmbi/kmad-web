from mock import patch
from nose.tools import eq_


def test_decode():
    data = '>1\nSAAAAAAEAAAAAAQAAAAAA\n>2\nSAAAAAAQAAAAAA\n'
    expected = '>1\nSEQ\n>2\nSQ'

    from kman_web.services.txtproc import decode

    result = decode(data, 7)
    eq_(result, expected)


def test_process_fasta():
    data = '>1\nSEQ\nSEQ\n'
    expected = '>1\nSEQSEQ'

    from kman_web.services.txtproc import process_fasta

    result = process_fasta(data)

    data = "SEQ\nSEQ\n"
    expected = ">fasta_header\nSEQSEQ"
    result = process_fasta(data)
    eq_(result, expected)


def test_preprocess():
    from kman_web.services.txtproc import preprocess

    # check spined
    data = 'S D 0.9\nE D 0.9\nQ O 0.9\n'
    expected = ['spine', [2, 2, 0]]
    result = preprocess(data, 'spine')
    eq_(result, expected)
    # check disopred
    data = '#\n#\n#\n   1 S * 0.9\n   2 E * 0.9\n   3 Q . 0.9\n'
    expected = ['disopred', [2, 2, 0]]
    result = preprocess(data, 'disopred')
    eq_(result, expected)
    # check psipred
    data = '#\n    \n' \
        + '   1 S C 0.9 0.1 0.1\n' \
        + '   2 E C 0.9 0.1 0.1\n' \
        + '   3 Q E 0.9 0.1 0.1\n'
    expected = ['psipred', [2, 2, 0]]
    result = preprocess(data, 'psipred')
    eq_(result, expected)
    # check predisorder
    data = 'SEQ\nDDO\n0.9 0.9 0.1\n'
    expected = ['predisorder', [2, 2, 0]]
    result = preprocess(data, 'predisorder')
    eq_(result, expected)


@patch('kman_web.services.txtproc.open', create=True)
def test_find_seqid_blast(mock_open):
    m_file = mock_open.return_value.__enter__.return_value

    from kman_web.services.txtproc import find_seqid_blast

    # check found
    m_file.read.return_value = open('tests/unit/testdata/test2.blastp').read()
    expected = [True, 'test']
    result = find_seqid_blast('testname')
    eq_(expected, result)
    # check not found
    m_file.read.return_value = open('tests/unit/testdata/test.blastp').read()
    expected = [False, '']
    result = find_seqid_blast('testname')
    eq_(expected, result)
