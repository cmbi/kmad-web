import logging
import os

from nose.tools import ok_

from kmad_web.domain.updaters.elm import ElmUpdater
from kmad_web.factory import create_app, create_celery_app

logging.basicConfig()
_log = logging.getLogger(__name__)


class TestElmUpdate(object):

    @classmethod
    def setup_class(cls):
        flask_app = create_app({'TESTING': True,
                                'CELERY_ALWAYS_EAGER': True})
        cls.celery = create_celery_app(flask_app)

    def test_elm_update(self):

        elm = ElmUpdater()
        elm.update()

        outfile = 'kmad_web/frontend/static/dbs/elm_complete.txt'
        # check if output file exists
        ok_(os.path.exists(outfile))

        # check if output file is not empty
        ok_(os.stat(outfile).st_size)
