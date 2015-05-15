from mock import patch, mock_open, call

from nose.tools import eq_, ok_
from MockResponse import MockResponse

from testdata import test_variables as test_vars


@patch('urllib2.urlopen')
@patch('kmad_web.services.convert.urllib2.Request')
@patch('kmad_web.services.convert.check_id')
@patch('kmad_web.services.convert.elm_db')
@patch('kmad_web.services.convert.tmp_fasta')
@patch('kmad_web.services.convert.read_fasta')
@patch('kmad_web.services.convert.find_phosph_sites')
@patch('kmad_web.services.convert.run_netphos')
@patch('kmad_web.services.convert.search_elm')
@patch('kmad_web.services.convert.run_pfam_scan')
@patch('kmad_web.services.convert.open', create=True)
def test_convert_to_7chars(mock_out_open, mock_run_pfam_scan,
                           mock_search_elm, mock_run_netphos,
                           mock_find_phosph_sites,
                           mock_read_fasta, mock_tmp_fasta,
                           mock_elm_db, mock_check_id,
                           mock_urlopen, mock_request):

    mock_urlopen.return_value = MockResponse('')

    filename = 'testdata/test.fasta'

    mock_read_fasta.return_value = ['>1', 'SEQ']

    # check: nothing to encode
    expected_data = '>1\nSAAAAAAEAAAAAAQAAAAAA\n' \
        + '## PROBABILITIES\n'
    mock_run_pfam_scan.return_value = [[], []]
    mock_search_elm.return_value = [[], [], []]
    mock_run_netphos.return_value = []
    mock_find_phosph_sites.return_value = [[], [], [], [], [], [], []]
    mock_tmp_fasta.return_value = 'tmp_filename'
    mock_elm_db.return_value = {'some_motif': {'GO': [], 'regex': 'KR.',
                                               'prob': 0.9}}
    mock_check_id.return_value = True

    from kmad_web.services.convert import convert_to_7chars

    convert_to_7chars(filename)
    expected_calls = [call('testdata/test.7c', 'w'),
                      call('testdata/test.map', 'w')]
    eq_(expected_calls, mock_out_open.call_args_list)
    handle = mock_out_open()
    expected_calls = [call(expected_data), call('')]
    eq_(expected_calls, handle.write.call_args_list)

    # check: encoded domain
    mock_run_pfam_scan.return_value = [[[1, 2]], ['some_domain']]
    expected_data = '>1\nSAaaAAAEAaaAAAQAAAAAA\n' \
        + '## PROBABILITIES\n'
    handle.reset_mock()

    convert_to_7chars(filename)
    expected_calls = [call(expected_data), call('domain_aa some_domain\n')]
    eq_(expected_calls, handle.write.call_args_list)

    # check: encoded motif
    mock_run_pfam_scan.return_value = [[], []]
    mock_search_elm.return_value = [[[1, 2]], ['some_motif'], [0.9]]
    expected_data = '>1\nSAAAAaaEAAAAaaQAAAAAA\n' \
        + '## PROBABILITIES\n' \
        + 'aa 0.9\n'
    handle.reset_mock()

    convert_to_7chars(filename)
    # handle.write.assert_called_once_with(expected_data)
    expected_calls = [call(expected_data), call('motif_aa some_motif KR.\n')]
    eq_(expected_calls, handle.write.call_args_list)

    # check: encoded PTMs
    mock_search_elm.return_value = [[], [], []]
    mock_find_phosph_sites.return_value = [[[1]], [[2]], [[3]], [], [], [], []]
    expected_data = '>1\nSAAAZAAEAAAVAAQAAARAA\n' \
        + '## PROBABILITIES\n'
    handle.reset_mock()

    convert_to_7chars(filename)
    # handle.write.assert_called_once_with(expected_data)
    expected_calls = [call(expected_data), call('')]
    eq_(expected_calls, handle.write.call_args_list)

    # check: encoded predicted phosph
    mock_run_netphos.return_value = [1]
    mock_find_phosph_sites.return_value = [[], [], [], [], [], [], []]
    expected_data = '>1\nSAAAdAAEAAAAAAQAAAAAA\n' \
        + '## PROBABILITIES\n'
    handle.reset_mock()

    convert_to_7chars(filename)
    # handle.write.assert_called_once_with(expected_data)
    expected_calls = [call(expected_data), call('')]
    eq_(expected_calls, handle.write.call_args_list)

    # check: check_id returns False
    mock_check_id.return_value = False
    mock_run_netphos.return_value = []
    mock_find_phosph_sites.return_value = [[[1]], [[2]], [[3]], [], [], [], []]
    expected_data = '>1\nSAAAAAAEAAAAAAQAAAAAA\n' \
        + '## PROBABILITIES\n'
    handle.reset_mock()

    convert_to_7chars(filename)
    # handle.write.assert_called_once_with(expected_data)
    expected_calls = [call(expected_data), call('')]
    eq_(expected_calls, handle.write.call_args_list)


@patch('urllib2.urlopen')
@patch('kmad_web.services.convert.urllib2.Request')
@patch('kmad_web.services.convert.os.path.exists')
@patch('kmad_web.services.convert.open',
       mock_open(read_data=open(
           'tests/unit/testdata/test_get_uniprot_txt.dat').read()),
       create=True)
def test_get_uniprot_txt(mock_os_path_exists, mock_urlopen, mock_request):
    mock_request.return_value = MockResponse(
        open('tests/unit/testdata/test_get_uniprot_txt.dat').read())
    # with open('tests/unit/testdata/features.dat') as a:
    #     expected = a.read().splitlines()
    mock_os_path_exists.return_value = True
    expected = {"features":
                ["FT   MOD_RES       2      2       N-acetylalanine."],
                "GO": ["0030424"]}

    from kmad_web.services.convert import get_uniprot_txt
    eq_(get_uniprot_txt('test_id'), expected)


@patch('urllib2.urlopen')
@patch('kmad_web.services.convert.urllib2.Request')
def test_search_elm(mock_request, mock_urlopen):

    # check: no motifs found
    mock_urlopen.return_value = MockResponse('')
    expected = [[], [], []]
    slims_classes = dict()
    seq_go_terms = ["007"]

    from kmad_web.services.convert import search_elm

    result = search_elm('TAU_HUMAN', test_vars.seq, slims_classes, seq_go_terms)
    eq_(result, expected)

    # check: found a motif
    data = "description\nMOTIF 1 1 False False False\n"
    mock_urlopen.return_value = MockResponse(data)
    slims_classes = dict({'MOTIF': {"prob": 1e-5, "GO": ["007"]}})
    expected = [[[1, 1]], ['MOTIF'], [0.8]]
    result = search_elm('TAU_HUMAN', test_vars.seq, slims_classes, seq_go_terms)
    eq_(result, expected)

    # check: found a motif but go terms don't overlap
    data = "description\nMOTIF 1 1 False False False\n"
    mock_urlopen.return_value = MockResponse(data)
    slims_classes = dict({'MOTIF': {"prob": 1e-5, "GO": ["008"]}})
    expected = [[], [], []]

    result = search_elm('TAU_HUMAN', test_vars.seq, slims_classes, seq_go_terms)
    eq_(result, expected)


def test_filter_out_overlappig():
    from kmad_web.services.convert import filter_out_overlapping

    lims = [[1, 2], [2, 3]]
    ids = ['MOTIF1', 'MOTIF2']
    probs = [0.8, 0.7]

    expected = ([[1, 2]], ['MOTIF1'], [0.8])
    result = filter_out_overlapping(lims, ids, probs)
    eq_(result, expected)


@patch('kmad_web.services.convert.get_uniprot_txt')
def test_find_phosph_sites(mock_uni_txt):
    from kmad_web.services.convert import get_uniprot_txt

    mock_uni_txt.return_value = {"features": open(
        'tests/unit/testdata/test_features.dat').readlines(),
        "GO": []}
    uniprot_txt = get_uniprot_txt('TEST_ID')
    expected = [[[2], [], [], []],
                [[7], [], [], []],
                [[6], [], [], []],
                [[4], [], [], []],
                [[1], [], [], []],
                [[5], [], [], []],
                [[3], [], [], []]]
    from kmad_web.services.convert import find_phosph_sites

    result = find_phosph_sites(uniprot_txt['features'])
    eq_(result, expected)


@patch('subprocess.check_output')
def test_run_netphos(mock_subprocess):
    mock_subprocess.return_value = open('tests/unit/testdata/test.np').read()

    from kmad_web.services.convert import run_netphos

    result = run_netphos('test')
    expected = [1]

    eq_(result, expected)


@patch('kmad_web.services.convert.open',
       mock_open(read_data=open(
           'tests/unit/testdata/TAU_HUMAN.fasta').read()),
       create=True)
def test_run_pfam_scan():
    from kmad_web.services.convert import run_pfam_scan
    expected = [[[560, 591], [592, 622], [623, 653], [654, 685]],
                ['PF00418.14', 'PF00418.14', 'PF00418.14', 'PF00418.14']]

    result = run_pfam_scan('test')
    eq_(result, expected)


def test_get_id():
    from kmad_web.services.convert import get_id

    header = 'TEST_HEADER'
    eq_(get_id(header), 'TEST_HEADER')

    header = 'test|HEADER|TEST_ID'
    eq_(get_id(header), 'TEST_ID')


@patch('kmad_web.services.convert.open',
       mock_open(read_data=open(
           'tests/unit/testdata/test_elm_classes_goterms.txt').read()),
       create=True)
def test_elm_db():
    from kmad_web.services.convert import elm_db
    expected = {'TEST_ID': {"prob": 0.003564849399,
                            "regex": "KR.",
                            "GO": ["007", "008"]}}

    eq_(elm_db(), expected)


@patch('kmad_web.services.convert.open',
       mock_open(read_data='>1\nSEQ\nSEQ\n>2\nSEQ\n'),
       create=True)
def test_read_fasta():
    expected = ['>1', 'SEQSEQ', '>2', 'SEQ']
    from kmad_web.services.convert import read_fasta

    eq_(read_fasta('testname'), expected)


@patch('urllib2.urlopen')
@patch('kmad_web.services.convert.urllib2.Request')
def test_check_id(mock_request, mock_urlopen):
    # check: no motifs found
    seq = ">1\nSEQ"
    seq_check = "SEQ"
    mock_urlopen.return_value = MockResponse(seq)

    from kmad_web.services.convert import check_id

    eq_(check_id('test_id', seq_check), True)

    seq = ">1\nSEQ"
    seq_check = "SEG"
    eq_(check_id('test_id', seq_check), False)
    seq = ">1\nSEQ"
    seq_check = "SEQ"

    import urllib2

    mock_urlopen.return_value = urllib2.Request("balbla")
    eq_(check_id('test_id', seq_check), False)


def test_check_id_without_mocks():
    from kmad_web.services.convert import check_id
    ok_(check_id('CRAM_CRAAB',
                 'TTCCPSIVARSNFNVCRLPGTPEALCATYTGCIIIPGATCPGDYAN'))
    ok_(not check_id('CRAM_CRAAB',
                     'PSIVARSNFNVCRLPGTPEALCATYTGCIIIPGATCPGDYAN'))
    ok_(not check_id('DUMMY_ID', 'SEQ'))


def test_get_annotation_level():
    from kmad_web.services.convert import get_annotation_level
    data = ['', '', '']
    eq_(get_annotation_level(data), 3)
    data = ['FT          ECO:0000269']
    eq_(get_annotation_level(data), 0)
    data = ['FT          ECO:0000269', 'FT          ECO:0000307']
    eq_(get_annotation_level(data), 0)
    data = ['FT          ECO:0000307']
    eq_(get_annotation_level(data), 2)
