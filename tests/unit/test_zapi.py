import json

from mock import patch
from nose.tools import eq_, ok_, raises

from kman_web.factory import create_app

class TestEndpoints(object):

    @classmethod
    def setup_class(cls):
        cls.flask_app = create_app({'TESTING': True,
                                    'SECRET_KEY': 'development_key',
                                    'WTF_CSRF_ENABLED': False})
        cls.app = cls.flask_app.test_client()

    @patch('kman_web.services.kman.PredictStrategy.__call__')
    def test_create_kman_predict(self, mock_call):
        mock_call.return_value = 12345
        rv = self.app.post('/api/create/predict/',
                           data={'data': 'testdata'})
        eq_(rv.status_code, 202)
        response = json.loads(rv.data)
        ok_('id' in response)
        eq_(response['id'], 12345)
        mock_call.assert_called_once_with('testdata')

    @patch('kman_web.services.kman.PredictAndAlignStrategy.__call__')
    def test_create_kman_predict(self, mock_call):
        mock_call.return_value = 12345
        rv = self.app.post('/api/create/predict_and_align/',
                           data={'data': 'testdata'})
        eq_(rv.status_code, 202)
        response = json.loads(rv.data)
        ok_('id' in response)
        eq_(response['id'], 12345)
        mock_call.assert_called_once_with('testdata')

    def test_create_kman_predict_no_data(self):
        rv = self.app.post('/api/create/predict/')
        eq_(rv.status_code, 400)

    def test_create_kman_predict_and_align_no_data(self):
        rv = self.app.post('/api/create/predict_and_align/')
        eq_(rv.status_code, 400)

    
    @raises(ValueError)
    def test_get_kman_status_unknown_input_type(self):
        rv = self.app.get('/api/status/unknown/12345/')
        eq_(rv.status_code, 400)
#
#    @raises(ValueError)
#    def test_get_kman_result_unknown_output_type(self):
#        rv = self.app.get('/api/result/unknown/12345/')
#        eq_(rv.status_code, 400)
#
