import os

from nose.tools import ok_

from kmad_web.services.alignment import (ClustaloService, ClustalwService,
                                         MafftService, MuscleService,
                                         TcoffeeService)


def test_clustalo_service():
    clustalo = ClustaloService()
    test_filename = "tests/unit/testdata/test_multi.fasta"
    out = clustalo.align(test_filename)
    ok_(os.path.exists(out))
    os.remove(out)


def test_clustalw_service():
    clustalw = ClustalwService()
    test_filename = "tests/unit/testdata/test_multi.fasta"
    out = clustalw.align(test_filename)
    ok_(os.path.exists(out))
    os.remove(out)


def test_mafft_service():
    mafft = MafftService()
    test_filename = "tests/unit/testdata/test_multi.fasta"
    out = mafft.align(test_filename)
    ok_(os.path.exists(out))
    os.remove(out)


def test_muscle_service():
    muscle = MuscleService()
    test_filename = "tests/unit/testdata/test_multi.fasta"
    out = muscle.align(test_filename)
    ok_(os.path.exists(out))
    os.remove(out)


def test_tcoffee_service():
    tcoffee = TcoffeeService()
    test_filename = "tests/unit/testdata/test_multi.fasta"
    out = tcoffee.align(test_filename)
    ok_(os.path.exists(out))
    os.remove(out)
