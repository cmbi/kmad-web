from mock import patch
from nose.tools import eq_, ok_


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
    # check globplot
    data = ">ts|000000|TEST_PROT|GlobDoms:|Disorder:1-3, 5-6\nSEQSEQSEQ\nSEQ"
    expected = ['globplot', [2, 2, 2, 0, 2, 2, 0, 0, 0, 0, 0, 0]]
    result = preprocess(data, 'globplot')
    eq_(result, expected)


@patch('kman_web.services.txtproc.open', create=True)
def test_find_seqid_blast(mock_open):
    m_file = mock_open.return_value.__enter__.return_value

    from kman_web.services.txtproc import find_seqid_blast

    # check found
    m_file.read.return_value = open('tests/unit/testdata/test.blastp').read()
    expected = [True, 'test']
    result = find_seqid_blast('testname')
    eq_(expected, result)
    # check not found
    m_file.read.return_value = open('tests/unit/testdata/test2.blastp').read()
    expected = [False, '']
    result = find_seqid_blast('testname')
    eq_(expected, result)


def test_check_if_multi():
    from kman_web.services.txtproc import check_if_multi

    testfasta = '>1\nSEQSEQ\nSEQ'
    ok_(not check_if_multi(testfasta))
    testfasta = '>1\nSEQSEQ\nSEQ\n>2\nSESESEQ\n'
    ok_(check_if_multi(testfasta))


def test_parse_features():
    from kman_web.services.txtproc import parse_features

    text_features = [{'featname': 'feat1', 'add_score': 2,
                      'sequence_number': '2',
                      'pattern': '',
                      'positions': '7,6,8-9'}]
    expected = 'feature_settings = \n  {\n' \
               + '  usr_features = ( \n' \
               + '{    name = "feat1";\n' \
               + '    tag = "";\n' \
               + '    add_score = 2;\n' \
               + '    subtract_score = "";\n' \
               + '    add_features = ("feat1");\n' \
               + '    add_tags = ();\n' \
               + '    add_exceptions = ();\n' \
               + '    subtract_features = ();\n' \
               + '    subtract_tags = ();\n' \
               + '    subtract_exceptions = ();\n' \
               + '    pattern = "";\n' \
               + '    positions = ( { seq = 2; pos = (7, 6, 8, 9); }\n' \
               + ');\n' \
               + '}\n' \
               + ');\n' \
               + '};\n'
    expected_list = expected.splitlines()
    result_list = parse_features(text_features).splitlines()
    for i in range(len(expected_list)):
        eq_(expected_list[i], result_list[i])
