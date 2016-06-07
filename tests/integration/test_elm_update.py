import logging
import os

from nose.tools import ok_

from kmad_web.factory import create_app, create_celery_app
# from kmad_web.services.types import ServiceError
logging.basicConfig()
_log = logging.getLogger(__name__)


class TestTasks(object):

    @classmethod
    def setup_class(cls):
        flask_app = create_app({'TESTING': True,
                                'CELERY_ALWAYS_EAGER': True})
        cls.celery = create_celery_app(flask_app)

    def test_elm_update(self):
        from kmad_web.tasks import update_elmdb

        update_elmdb()

        outfile = 'kmad_web/frontend/static/dbs/elm_complete.txt'
        # check if output file exists
        ok_(os.path.exists(outfile))

        # check if output file is not empty
        ok_(os.stat(outfile).st_size)
