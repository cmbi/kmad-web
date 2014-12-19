from mock import patch, mock_open

from nose.tools import eq_
from MockResponse import MockResponse

from testdata import test_variables as test_vars


@patch('kman_web.services.convert.elm_db')
@patch('kman_web.services.convert.tmp_fasta')
@patch('kman_web.services.convert.read_fasta')
@patch('kman_web.services.convert.find_phosph_sites')
@patch('kman_web.services.convert.run_netphos')
@patch('kman_web.services.convert.search_elm')
@patch('kman_web.services.convert.run_pfam_scan')
@patch('kman_web.services.convert.open', create=True)
def test_convert_to_7chars(mock_out_open, mock_run_pfam_scan,
                           mock_search_elm, mock_run_netphos,
                           mock_find_phosph_sites,
                           mock_read_fasta, mock_tmp_fasta,
                           mock_elm_db):

    filename = 'testdata/test.fasta'
    expected_outname = 'testdata/test.7c'

    mock_read_fasta.return_value = ['>1', 'SEQ']

    # check: nothing to encode
    expected_data = '>1\nSAAAAAAEAAAAAAQAAAAAA\n' \
        + '## PROBABILITIES\n' \
        + 'motif probability\n'
    mock_run_pfam_scan.return_value = [[], []]
    mock_search_elm.return_value = [[], [], []]
    mock_run_netphos.return_value = []
    mock_find_phosph_sites.return_value = [[], [], [], [], [], [], []]
    mock_tmp_fasta.return_value = 'tmp_filename'
    mock_elm_db.return_value = 'elm_db'

    from kman_web.services.convert import convert_to_7chars

    convert_to_7chars(filename)

    mock_out_open.assert_called_once_with(expected_outname, 'w')
    handle = mock_out_open()
    handle.write.assert_called_once_with(expected_data)

    # check: encoded domain
    mock_run_pfam_scan.return_value = [[[1, 2]], ['domain']]
    expected_data = '>1\nSAaaAAAEAaaAAAQAAAAAA\n' \
        + '## PROBABILITIES\n' \
        + 'motif index  probability\n'
    handle.reset_mock()

    convert_to_7chars(filename)
    handle.write.assert_called_once_with(expected_data)

    # check: encoded motif
    mock_run_pfam_scan.return_value = [[], []]
    mock_search_elm.return_value = [[[1, 2]], ['MOTIF'], [0.9]]
    expected_data = '>1\nSAAAAaaEAAAAaaQAAAAAA\n' \
        + '## PROBABILITIES\n' \
        + 'motif index  probability\naa 0.9\n'
    handle.reset_mock()

    convert_to_7chars(filename)
    handle.write.assert_called_once_with(expected_data)

    # check: encoded PTMs
    mock_search_elm.return_value = [[], [], []]
    mock_find_phosph_sites.return_value = [[[1]], [[2]], [[3]], [], [], [], []]
    expected_data = '>1\nSAAAZAAEAAAVAAQAAARAA\n' \
        + '## PROBABILITIES\n' \
        + 'motif index  probability\n'
    handle.reset_mock()

    convert_to_7chars(filename)
    handle.write.assert_called_once_with(expected_data)

    # check: encoded predicted phosph
    mock_run_netphos.return_value = [1]
    mock_find_phosph_sites.return_value = [[], [], [], [], [], [], []]
    expected_data = '>1\nSAAAdAAEAAAAAAQAAAAAA\n' \
        + '## PROBABILITIES\n' \
        + 'motif index  probability\n'
    handle.reset_mock()

    convert_to_7chars(filename)
    handle.write.assert_called_once_with(expected_data)


@patch('kman_web.services.convert.open',
       mock_open(read_data=open('tests/unit/testdata/TEST.dat').read()),
       create=True)
def test_get_uniprot_txt():
    with open('tests/unit/testdata/features.dat') as a:
        expected = a.read().splitlines()

    from kman_web.services.convert import get_uniprot_txt
    eq_(get_uniprot_txt('test_id'), expected)


@patch('urllib2.urlopen')
@patch('kman_web.services.convert.urllib2.Request')
def test_search_elm(mock_request, mock_urlopen):

    # check: no motifs found
    mock_urlopen.return_value = MockResponse('')
    expected = [[], [], []]
    slims_classes = dict()

    from kman_web.services.convert import search_elm

    result = search_elm('TAU_HUMAN', test_vars.seq, slims_classes)
    eq_(result, expected)

    # check: found a motif
    data = "MOTIF 1 1 False False False\n"
    mock_urlopen.return_value = MockResponse(data)
    slims_classes = dict({'MOTIF': [1e-5, ""]})
    expected = [[[1, 1]], ['MOTIF'], [0.8]]

    result = search_elm('TAU_HUMAN', test_vars.seq, slims_classes)
    eq_(result, expected)


def test_filter_out_overlappig():
    from kman_web.services.convert import filter_out_overlapping

    lims = [[1, 2], [2, 3]]
    ids = ['MOTIF1', 'MOTIF2']
    probs = [0.8, 0.7]

    expected = ([[1, 2]], ['MOTIF1'], [0.8])
    result = filter_out_overlapping(lims, ids, probs)
    eq_(result, expected)


@patch('kman_web.services.convert.get_uniprot_txt')
def test_find_phosph_sites(mock_uni_txt):
    mock_uni_txt.return_value = open('tests/unit/testdata/test_features.dat').readlines()
    expected = [[[2], [], [], []],
                [[7], [], [], []],
                [[6], [], [], []],
                [[4], [], [], []],
                [[1], [], [], []],
                [[5], [], [], []],
                [[3], [], [], []]]
    from kman_web.services.convert import find_phosph_sites

    result = find_phosph_sites('TEST_ID')
    eq_(result, expected)


@patch('subprocess.check_output')
def test_run_netphos(mock_subprocess):
    mock_subprocess.return_value = open('tests/unit/testdata/test.np').read()

    from kman_web.services.convert import run_netphos

    result = run_netphos('test')
    expected = [1]

    eq_(result, expected)


@patch('subprocess.check_output')
def test_run_pfam_scan(mock_subprocess):
    mock_subprocess.return_value = open('tests/unit/testdata/test.pfam').read()
    from kman_web.services.convert import run_pfam_scan
    expected = [[[1, 2]], ['TEST_ACC TEST_NAME']]

    result = run_pfam_scan('test')
    eq_(result, expected)


def test_get_id():
    from kman_web.services.convert import get_id

    header = 'TEST_HEADER'
    eq_(get_id(header), 'UNKNOWN_ID')

    header = 'test|HEADER|TEST_ID'
    eq_(get_id(header), 'TEST_ID')


@patch('kman_web.services.convert.open',
       mock_open(read_data=open('tests/unit/testdata/test_elm_classes.tsv').read()),
       create=True)
def test_elm_db():
    from kman_web.services.convert import elm_db
    expected = {'TEST_ID': [0.003564849399,
                            '"TEST_ACC"\t"TEST_ID"\t"description"\t'
                            + '"TESTREGEX"\t"0.003564849399"\t"39"\t"0"']}

    eq_(elm_db(), expected)


@patch('kman_web.services.convert.open',
       mock_open(read_data='>1\nSEQ\nSEQ\n>2\nSEQ\n'),
       create=True)
def test_read_fasta():
    expected = ['>1', 'SEQSEQ', '>2', 'SEQ']
    from kman_web.services.convert import read_fasta

    eq_(read_fasta('testname'), expected)
