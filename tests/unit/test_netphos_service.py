import subprocess

from mock import patch
from nose.tools import assert_raises, eq_

from kmad_web.services.netphos import NetphosService
from kmad_web.services.types import ServiceError


@patch('kmad_web.services.netphos.subprocess.check_output')
def test_predict_success(mock_check_output):
    mock_check_output.return_value = "Netphos result"
    netphos = NetphosService("/usr/local/bin/netphos")
    test_filename = "tests/unit/testdata/test.fasta"
    eq_("Netphos result", netphos.predict(test_filename))


@patch('kmad_web.services.netphos.subprocess.check_output')
def test_predict_subprocess_error(mock_check_output):
    mock_check_output.side_effect = subprocess.CalledProcessError(1, "netphos")
    netphos = NetphosService("/usr/local/bin/netphos")
    test_filename = "tests/unit/testdata/test.fasta"
    assert_raises(ServiceError, netphos.predict, test_filename)


def test_predict_file_not_found():
    netphos = NetphosService("/usr/local/bin/netphos")
    test_filename = "tests/unit/testdata/test.fasta_nonexistent"
    assert_raises(ServiceError, netphos.predict, test_filename)
