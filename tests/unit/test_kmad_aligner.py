from mock import patch, PropertyMock

from nose.tools import eq_, with_setup, assert_raises

from kmad_web.services.helpers.cache import cache_manager as cm
from kmad_web.services.types import ServiceError
from kmad_web.default_settings import KMAD


def setup():
    cm.load_config({
        'redis': {'redis.backend': 'dogpile.cache.null'}
    })


def teardown():
    cm.reset()


@patch('kmad_web.services.kmad_aligner.open')
@patch('kmad_web.services.kmad_aligner.tempfile.NamedTemporaryFile')
@patch('kmad_web.services.kmad_aligner.subprocess.call')
@with_setup(setup, teardown)
def test_kmad_aligner(mock_call, mock_temp, mock_open):

    from kmad_web.services.kmad_aligner import kmad

    type(mock_temp.return_value).name = PropertyMock(return_value='tempname')

    eq_('tempname_al', kmad.align('', '', '', '', '', '', '', '', '', '', ''))
    mock_call.reset_mock()

    kmad.align('', '', '', '', '', '', '', 'path', True,
               False, True)
    args = [KMAD, '-i', 'tempname', '-o', 'tempname', '-g', '',
            '-e', '', '-n', '', '-p', '', '-m', '',
            '-d', '', '--out-encoded', '-c', '7', '--conf', 'path',
            '--refine', '--gapped']
    mock_call.assert_called_once_with(args, stderr=-1)
    mock_call.reset_mock()

    kmad.align('', '', '', '', '', '', '', 'path', False,
               True, True)
    args = [KMAD, '-i', 'tempname', '-o', 'tempname', '-g', '', '-e', '',
            '-n', '', '-p', '', '-m', '', '-d', '', '--out-encoded', '-c', '7',
            '--conf', 'path', '--refine', '--full_ungapped']
    mock_call.assert_called_once_with(args, stderr=-1)
    mock_call.reset_mock()

    assert_raises(ServiceError, kmad.align, '', '', '', '', '', '', '', '',
                  '', '', '')


@patch('kmad_web.services.kmad_aligner.tempfile.NamedTemporaryFile')
@with_setup(setup, teardown)
def test_kmad_aligner_error(mock_temp):

    from kmad_web.services.kmad_aligner import kmad

    type(mock_temp.return_value).name = PropertyMock(return_value='tempname')
    assert_raises(ServiceError, kmad.align, '', '', '', '', '', '', '', '',
                  '', '', '')
