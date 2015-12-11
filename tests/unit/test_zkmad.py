from mock import patch, PropertyMock, Mock
from nose.tools import eq_, assert_raises

from kmad_web.services.kmad import (AnnotateStrategy, MotifsStrategy, PtmsStrategy,
                                    AlignStrategy, PredictStrategy,
                                    PredictAndAlignStrategy, RefineStrategy)


@patch('kmad_web.services.kmad.chain.__call__')
def test_motifs_strategy(mock_chain):
    test_id = '12345'
    type(mock_chain.return_value).id = PropertyMock(return_value=test_id)
    s = MotifsStrategy('SEQ', '1', 'A')
    eq_(test_id, s())
    s = MotifsStrategy('>1\nSEQ', '1', 'A')
    eq_(test_id, s())


@patch('kmad_web.services.kmad.chain.__call__')
def test_ptms_strategy(mock_chain):
    test_id = '12345'
    type(mock_chain.return_value).id = PropertyMock(return_value=test_id)
    s = PtmsStrategy('SEQ', '1', 'A')
    eq_(test_id, s())
    s = PtmsStrategy('>1\nSEQ', '1', 'A')
    eq_(test_id, s())


@patch('kmad_web.services.kmad.tempfile.NamedTemporaryFile')
@patch('kmad_web.services.kmad.chord.__call__')
@patch('kmad_web.services.kmad.chain.__call__')
def test_predict_strategy(mock_chain, mock_group, mock_temp):
    test_id = '12345'
    type(mock_chain.return_value).id = PropertyMock(return_value=test_id)
    s = PredictStrategy('SEQ', ['d2p2'])
    s()
    s = PredictStrategy('>1\nSEQ', ['other_method'])
    s()


@patch('kmad_web.services.kmad.chain.__call__')
@patch('kmad_web.services.kmad.UserFeaturesParser.write_conf_file')
def test_align_strategy(mock_conf, mock_chain):
    mock_conf.return_value = 'conf_path'
    test_id = '12345'
    type(mock_chain.return_value).id = PropertyMock(return_value=test_id)
    s = AlignStrategy('>1\nSEQ', '', '', '', '', '', '', '', '', '')
    eq_(test_id, s())

    s = AlignStrategy('>1\nSEQ\n>2\nSEQSEQ', '', '', '', '', '', '', '', '', '')
    eq_(test_id, s())


@patch('kmad_web.services.kmad.chain.__call__')
@patch('kmad_web.services.kmad.UserFeaturesParser.write_conf_file')
def test_refine_strategy(mock_conf, mock_chain):
    mock_conf.return_value = 'conf_path'
    test_id = '12345'
    type(mock_chain.return_value).id = PropertyMock(return_value=test_id)
    s = RefineStrategy('>1\nSEQ', '', '', '', '', '', '', '', '',
                       'aligment_method')
    eq_(test_id, s())

    s = RefineStrategy('>1\nSEQ\n>2\nSEQSEQ', '', '', '', '', '', '', '', '')
    eq_(test_id, s())

    s = RefineStrategy('>1\nSEQ\n>2\nSEQSEQ', '', '', '', '', '', '', '', '',
                       'alignment_method')
    eq_(test_id, s())

    s = RefineStrategy('>1\nSEQ', '', '', '', '', '', '', '', '')
    assert_raises(RuntimeError, s)


def test_annotate_strategy():
    test_id = '12345'
    import sys
    mock_tasks = Mock()
    mock_tasks.annotate = Mock()
    sys.modules['kmad_web.tasks'] = mock_tasks
    mock_tasks.annotate.delay.return_value.id = test_id
    s = AnnotateStrategy('>1\nseqseq\nseq\n>2\nseq---\n---')
    eq_(test_id, s())


@patch('kmad_web.services.kmad.group.__call__')
@patch('kmad_web.services.kmad.chain.__call__')
@patch('kmad_web.services.kmad.UserFeaturesParser.write_conf_file')
def test_predict_and_align(mock_conf, mock_chain, mock_group):
    mock_conf.return_value = 'conf_path'
    test_id = '12345'
    type(mock_chain.return_value).id = PropertyMock(return_value=test_id)
    s = PredictAndAlignStrategy('>1\nSEQ', ['d2p2'], '', '', '', '', '', '', '',
                                '', '')
    eq_(test_id, s())

    s = PredictAndAlignStrategy('>1\nSEQ\n>2\nSEQSEQ', ['d2p2'], '', '', '', '',
                                '', '', '', '', '')
    eq_(test_id, s())

    s = PredictAndAlignStrategy('>1\nSEQ\n>2\nSEQSEQ', ['other_method'], '', '',
                                '', '', '', '', '', '', '')
    eq_(test_id, s())
