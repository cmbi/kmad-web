import os

from nose.tools import ok_, assert_raises, with_setup

from kmad_web.default_settings import CLUSTALO, CLUSTALW, MAFFT, MUSCLE, TCOFFEE
from kmad_web.services.alignment import (ClustaloService, ClustalwService,
                                         MafftService, MuscleService,
                                         TcoffeeService)
from kmad_web.services.types import ServiceError
from kmad_web.services.helpers.cache import cache_manager as cm


def setup():
    cm.load_config({
        'redis': {'redis.backend': 'dogpile.cache.null'}
    })


def teardown():
    cm.reset()


@with_setup(setup, teardown)
def test_clustalo_service():
    if not os.path.exists(CLUSTALO):
        return
    clustalo = ClustaloService()
    test_filename = "tests/unit/testdata/test_multi.fasta"
    out = clustalo.align(test_filename)
    ok_(os.path.exists(out))
    os.remove(out)

    clustalo._path = "NONAME"
    assert_raises(ServiceError, clustalo.align, test_filename)


@with_setup(setup, teardown)
def test_clustalw_service():
    if not os.path.exists(CLUSTALW):
        return
    clustalw = ClustalwService()
    test_filename = "tests/unit/testdata/test_multi.fasta"
    dnd = "tests/unit/testdata/test_multi.dnd"
    out = clustalw.align(test_filename)
    ok_(os.path.exists(out))
    os.remove(out)
    os.remove(dnd)

    clustalw._path = "NONAME"
    assert_raises(ServiceError, clustalw.align, test_filename)


@with_setup(setup, teardown)
def test_mafft_service():
    if not os.path.exists(MAFFT):
        return
    mafft = MafftService()
    test_filename = "tests/unit/testdata/test_multi.fasta"
    out = mafft.align(test_filename)
    ok_(os.path.exists(out))
    os.remove(out)

    mafft._path = "NONAME"
    assert_raises(ServiceError, mafft.align, test_filename)


@with_setup(setup, teardown)
def test_muscle_service():
    if not os.path.exists(MUSCLE):
        return
    muscle = MuscleService()
    test_filename = "tests/unit/testdata/test_multi.fasta"
    out = muscle.align(test_filename)
    ok_(os.path.exists(out))
    os.remove(out)

    muscle._path = "NONAME"
    assert_raises(ServiceError, muscle.align, test_filename)


@with_setup(setup, teardown)
def test_tcoffee_service():
    if not os.path.exists(TCOFFEE):
        return
    tcoffee = TcoffeeService()
    test_filename = "tests/unit/testdata/test_multi.fasta"
    out = tcoffee.align(test_filename)
    ok_(os.path.exists(out))
    os.remove(out)

    tcoffee._path = "NONAME"
    assert_raises(ServiceError, tcoffee.align, test_filename)
