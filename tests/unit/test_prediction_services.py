from mock import Mock, mock_open, patch, PropertyMock

from nose.tools import eq_, assert_raises, with_setup

from kmad_web.services.disopred import disopred
from kmad_web.services.types import ServiceError
from kmad_web.services.helpers.cache import cache_manager as cm


def setup():
    cm.load_config({
        'redis': {'redis.backend': 'dogpile.cache.null'}
    })


def teardown():
    cm.reset()


@patch('kmad_web.services.disopred.os.stat')
@patch('kmad_web.services.disopred.os.remove')
@patch('kmad_web.services.disopred.os.path.exists')
@patch('kmad_web.services.disopred.subprocess.call')
@patch('kmad_web.services.disopred.open', mock_open(read_data='prediction'),
       create=True)
@with_setup(setup, teardown)
def test_disopred_service(mock_call, mock_exists, mock_remove, mock_stat):
    mock_exists.return_value = True
    mock_stat.return_value = Mock()
    type(mock_stat.return_value).st_size = PropertyMock(return_value=0)

    expected = 'prediction'
    eq_(expected, disopred('>1\nSEQ'))

    mock_exists.return_value = False
    assert_raises(ServiceError, disopred, '>1\nSEQ')


@patch('kmad_web.services.psipred.os.stat')
@patch('kmad_web.services.psipred.os.remove')
@patch('kmad_web.services.psipred.os.path.exists')
@patch('kmad_web.services.psipred.subprocess.call')
@patch('kmad_web.services.psipred.open', mock_open(read_data='prediction'),
       create=True)
@with_setup(setup, teardown)
def test_psipred_service(mock_call, mock_exists, mock_remove, mock_stat):
    from kmad_web.services.psipred import psipred
    mock_exists.return_value = True
    mock_stat.return_value = Mock()
    type(mock_stat.return_value).st_size = PropertyMock(return_value=0)
    expected = 'prediction'
    eq_(expected, psipred('fasta_path'))

    mock_exists.return_value = False
    assert_raises(ServiceError, psipred, 'fasta_path')


@patch('kmad_web.services.predisorder.os.stat')
@patch('kmad_web.services.predisorder.os.remove')
@patch('kmad_web.services.predisorder.os.path.exists')
@patch('kmad_web.services.predisorder.subprocess.call')
@patch('kmad_web.services.predisorder.open', mock_open(read_data='prediction'),
       create=True)
@with_setup(setup, teardown)
def test_predisorder_service(mock_call, mock_exists, mock_remove, mock_stat):
    from kmad_web.services.predisorder import predisorder
    mock_exists.return_value = True
    mock_stat.return_value = Mock()
    type(mock_stat.return_value).st_size = PropertyMock(return_value=0)
    expected = 'prediction'
    eq_(expected, predisorder('fasta_path'))

    mock_exists.return_value = False
    assert_raises(ServiceError, predisorder, 'fasta_path')


@patch('kmad_web.services.globplot.os.stat')
@patch('kmad_web.services.globplot.os.remove')
@patch('kmad_web.services.globplot.subprocess.check_output')
@with_setup(setup, teardown)
def test_globplot_service(mock_check_output, mock_rmeove, mock_stat):
    from kmad_web.services.globplot import globplot
    mock_check_output.return_value = '>globplot result'
    mock_stat.return_value = Mock()
    type(mock_stat.return_value).st_size = PropertyMock(return_value=0)
    expected = '>globplot result'
    eq_(expected, globplot('fasta_path'))

    mock_check_output.return_value = None
    assert_raises(ServiceError, globplot, 'fasta_path')


@patch('kmad_web.services.iupred.os.stat')
@patch('kmad_web.services.iupred.os.remove')
@patch('kmad_web.services.iupred.subprocess.check_output')
@with_setup(setup, teardown)
def test_iupred_service(mock_check_output, mock_remove, mock_stat):
    from kmad_web.services.iupred import iupred
    mock_check_output.return_value = 'iupred result'
    mock_stat.return_value = Mock()
    type(mock_stat.return_value).st_size = PropertyMock(return_value=0)
    expected = 'iupred result'
    eq_(expected, iupred('fasta_path'))

    mock_check_output.return_value = None
    assert_raises(ServiceError, iupred, 'fasta_path')


@patch('kmad_web.services.spined.os.stat')
@patch('kmad_web.services.spined.os.remove')
@patch('kmad_web.services.spined.os.path.exists')
@patch('kmad_web.services.spined.subprocess.call')
@patch('kmad_web.services.spined.open', mock_open(read_data='prediction'),
       create=True)
@with_setup(setup, teardown)
def test_spined_service(mock_call, mock_exists, mock_remove, mock_stat):
    from kmad_web.services.spined import spined
    mock_exists.return_value = True
    mock_stat.return_value = Mock()
    type(mock_stat.return_value).st_size = PropertyMock(return_value=0)
    expected = 'prediction'
    eq_(expected, spined('fasta_path'))

    mock_exists.return_value = False
    assert_raises(ServiceError, spined, 'fasta_path')
