import os

from nose.tools import ok_, assert_raises

from kmad_web.services.alignment import (ClustaloService, ClustalwService,
                                         MafftService, MuscleService,
                                         TcoffeeService)
from kmad_web.services.types import ServiceError


def test_clustalo_service():
    clustalo = ClustaloService()
    test_filename = "tests/unit/testdata/test_multi.fasta"
    out = clustalo.align(test_filename)
    ok_(os.path.exists(out))
    os.remove(out)

    clustalo._path = "NONAME"
    assert_raises(ServiceError, clustalo.align, test_filename)


def test_clustalw_service():
    clustalw = ClustalwService()
    test_filename = "tests/unit/testdata/test_multi.fasta"
    dnd = "tests/unit/testdata/test_multi.dnd"
    out = clustalw.align(test_filename)
    ok_(os.path.exists(out))
    os.remove(out)
    os.remove(dnd)

    clustalw._path = "NONAME"
    assert_raises(ServiceError, clustalw.align, test_filename)


def test_mafft_service():
    mafft = MafftService()
    test_filename = "tests/unit/testdata/test_multi.fasta"
    out = mafft.align(test_filename)
    ok_(os.path.exists(out))
    os.remove(out)

    mafft._path = "NONAME"
    assert_raises(ServiceError, mafft.align, test_filename)


def test_muscle_service():
    muscle = MuscleService()
    test_filename = "tests/unit/testdata/test_multi.fasta"
    out = muscle.align(test_filename)
    ok_(os.path.exists(out))
    os.remove(out)

    muscle._path = "NONAME"
    assert_raises(ServiceError, muscle.align, test_filename)


def test_tcoffee_service():
    tcoffee = TcoffeeService()
    test_filename = "tests/unit/testdata/test_multi.fasta"
    out = tcoffee.align(test_filename)
    ok_(os.path.exists(out))
    os.remove(out)

    tcoffee._path = "NONAME"
    assert_raises(ServiceError, tcoffee.align, test_filename)
