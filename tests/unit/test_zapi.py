import inspect
import json
import re

from mock import patch
from nose.tools import eq_, ok_

from kmad_web.factory import create_app


class TestEndpoints(object):

    @classmethod
    def setup_class(cls):
        cls.flask_app = create_app({'TESTING': True,
                                    'SECRET_KEY': 'development_key',
                                    'WTF_CSRF_ENABLED': False,
                                    'KMAD_WEB_SETTINGS': '../dev_settings.py'})
        cls.app = cls.flask_app.test_client()

    @patch('kmad_web.services.kmad.AlignStrategy.__call__')
    def test_create_kmad_align(self, mock_call):
        mock_call.return_value = 12345
        rv = self.app.post('/api/create/align/',
                           data={'seq_data': 'testdata',
                                 'gop': -1, 'gep': -1,
                                 'egp': -1, 'ptm_score': 1,
                                 'domain_score': 1, 'motif_score': 1,
                                 'usr_features': ['test'],
                                 'output_type': 'align',
                                 'gapped': False, 'seq_limit': 35})
        response = json.loads(rv.data)
        eq_(rv.status_code, 202)
        ok_('id' in response)
        eq_(response['id'], 12345)
        mock_call.assert_called_once_with()

    @patch('kmad_web.services.kmad.PredictStrategy.__call__')
    def test_create_kmad_predict(self, mock_call):
        mock_call.return_value = 12345
        methods = 'testmethod1 testmethod2'
        rv = self.app.post('/api/create/predict/',
                           data={'seq_data': 'testdata',
                                 'prediction_methods': methods})

        eq_(rv.status_code, 202)
        response = json.loads(rv.data)
        ok_('id' in response)
        eq_(response['id'], 12345)
        mock_call.assert_called_once_with()

    def test_create_kmad_predict_no_data(self):
        rv = self.app.post('/api/create/predict/')
        eq_(rv.status_code, 400)

    def test_create_kmad_align_no_data(self):
        rv = self.app.post('/api/create/align/')
        eq_(rv.status_code, 400)

    def test_api_docs(self):
        from kmad_web.frontend.api import endpoints

        rv = self.app.get('/api/')
        eq_(rv.status_code, 200)
        excluded_fs = ['api_docs', 'api_example', 'download_api_example',
                       'create', 'get_result']
        for f_name, f in inspect.getmembers(endpoints, inspect.isfunction):
            mod_name = inspect.getmodule(f).__name__
            if "kmad_web.frontend.api.endpoints" in mod_name and \
               f_name not in excluded_fs:
                src = inspect.getsourcelines(f)
                rx = r"@bp\.route\('([\w\/<>]*)', methods=\['([A-Z]*)']\)"
                m = re.search(rx, src[0][0])
                url = m.group(1)
                url = url.replace('>', '&gt;')
                url = url.replace('<', '&lt;')
                assert "<samp>/api{}</samp>".format(url) in rv.data
