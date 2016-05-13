import os
import subprocess

from mock import patch
from nose.tools import assert_raises, eq_, with_setup

from kmad_web.default_settings import NETPHOS_PATH
from kmad_web.services.netphos import NetphosService
from kmad_web.services.types import ServiceError
from kmad_web.services.helpers.cache import cache_manager as cm


def setup():
    cm.load_config({
        'redis': {'redis.backend': 'dogpile.cache.null'}
    })


def teardown():
    cm.reset()


@patch('kmad_web.services.netphos.subprocess.check_output')
@with_setup(setup, teardown)
def test_predict_success(mock_check_output):
    if not os.path.exists(NETPHOS_PATH):
        return
    mock_check_output.return_value = "Netphos result"

    netphos = NetphosService(NETPHOS_PATH)
    test_fasta = ">1\nSEQ"
    eq_("Netphos result", netphos.predict(test_fasta))


@patch('kmad_web.services.netphos.os.remove')
@patch('kmad_web.services.netphos.os.path.exists')
@patch('kmad_web.services.netphos.subprocess.check_output')
@with_setup(setup, teardown)
def test_predict(mock_check_output, mock_exists, mock_rm):
    mock_exists.return_value = True
    mock_check_output.return_value = "Netphos result"

    netphos = NetphosService(NETPHOS_PATH)
    test_fasta = ">1\nSEQ"
    eq_("Netphos result", netphos.predict(test_fasta))

    mock_exists.return_value = False
    assert_raises(ServiceError, netphos.predict, test_fasta)


@patch('kmad_web.services.netphos.subprocess.check_output')
@with_setup(setup, teardown)
def test_predict_subprocess_error(mock_check_output):
    if not os.path.exists(NETPHOS_PATH):
        return
    mock_check_output.side_effect = subprocess.CalledProcessError(1, "netphos")
    netphos = NetphosService(NETPHOS_PATH)
    test_fasta = ">1\nSEQ"
    assert_raises(ServiceError, netphos.predict, test_fasta)
