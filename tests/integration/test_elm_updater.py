import os

from nose.tools import ok_, with_setup

from kmad_web.domain.updaters.elm import ElmUpdater
from kmad_web.services.helpers.cache import cache_manager as cm


def setup():
    cm.load_config({
        'redis': {'redis.backend': 'dogpile.cache.null'}
    })


def teardown():
    cm.reset()


@with_setup(setup, teardown)
def test_elm_updater():
    elm = ElmUpdater()
    elm.update()
    ok_(os.path.exists('kmad_web/frontend/static/dbs/elm_complete.txt'))
