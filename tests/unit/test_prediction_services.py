from mock import mock_open, patch

from nose.tools import eq_, assert_raises, with_setup

from kmad_web.services.types import ServiceError
from kmad_web.services.helpers.cache import cache_manager as cm


def setup():
    cm.load_config({
        'redis': {'redis.backend': 'dogpile.cache.null'}
    })


def teardown():
    cm.reset()


@patch('kmad_web.services.disopred.os.path.exists')
@patch('kmad_web.services.disopred.subprocess.call')
@patch('kmad_web.services.disopred.open', mock_open(read_data='prediction'),
       create=True)
@with_setup(setup, teardown)
def test_disopred_service(mock_call, mock_exists):
    from kmad_web.services.disopred import disopred
    mock_exists.return_value = True
    expected = 'prediction'
    eq_(expected, disopred('fasta_path'))

    mock_exists.return_value = False
    assert_raises(ServiceError, disopred, 'fasta_path')


@patch('kmad_web.services.psipred.os.path.exists')
@patch('kmad_web.services.psipred.subprocess.call')
@patch('kmad_web.services.psipred.open', mock_open(read_data='prediction'),
       create=True)
@with_setup(setup, teardown)
def test_psipred_service(mock_call, mock_exists):
    from kmad_web.services.psipred import psipred
    mock_exists.return_value = True
    expected = 'prediction'
    eq_(expected, psipred('fasta_path'))

    mock_exists.return_value = False
    assert_raises(ServiceError, psipred, 'fasta_path')


@patch('kmad_web.services.predisorder.os.path.exists')
@patch('kmad_web.services.predisorder.subprocess.call')
@patch('kmad_web.services.predisorder.open', mock_open(read_data='prediction'),
       create=True)
@with_setup(setup, teardown)
def test_predisorder_service(mock_call, mock_exists):
    from kmad_web.services.predisorder import predisorder
    mock_exists.return_value = True
    expected = 'prediction'
    eq_(expected, predisorder('fasta_path'))

    mock_exists.return_value = False
    assert_raises(ServiceError, predisorder, 'fasta_path')


@patch('kmad_web.services.globplot.subprocess.check_output')
@with_setup(setup, teardown)
def test_globplot_service(mock_check_output):
    from kmad_web.services.globplot import globplot
    mock_check_output.return_value = 'globplot result'
    expected = 'globplot result'
    eq_(expected, globplot('fasta_path'))

    mock_check_output.return_value = None
    assert_raises(ServiceError, globplot, 'fasta_path')


@patch('kmad_web.services.iupred.subprocess.check_output')
@with_setup(setup, teardown)
def test_iupred_service(mock_check_output):
    from kmad_web.services.iupred import iupred
    mock_check_output.return_value = 'iupred result'
    expected = 'iupred result'
    eq_(expected, iupred('fasta_path'))

    mock_check_output.return_value = None
    assert_raises(ServiceError, iupred, 'fasta_path')


@patch('kmad_web.services.spined.os.path.exists')
@patch('kmad_web.services.spined.subprocess.call')
@patch('kmad_web.services.spined.open', mock_open(read_data='prediction'),
       create=True)
@with_setup(setup, teardown)
def test_spined_service(mock_call, mock_exists):
    from kmad_web.services.spined import spined
    mock_exists.return_value = True
    expected = 'prediction'
    eq_(expected, spined('fasta_path'))

    mock_exists.return_value = False
    assert_raises(ServiceError, spined, 'fasta_path')
