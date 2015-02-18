from mock import patch

from nose.tools import eq_

from kman_web.factory import create_app


class TestDashboard(object):

    @classmethod
    def setup_class(cls):
        cls.flask_app = create_app({'TESTING': True,
                                    'SECRET_KEY': 'development_key',
                                    'WTF_CSRF_ENABLED': False})
        cls.app = cls.flask_app.test_client()

    def test_index(self):
        rv = self.app.get('/')
        eq_(rv.status_code, 200)

    @patch('kman_web.services.kman.PredictStrategy.__call__')
    @patch('kman_web.services.kman.PredictAndAlignStrategy.__call__')
    def test_index_post_predict(self, mock_call1, mock_call2):
        mock_call1.return_value = 12345
        mock_call2.return_value = 12345
        test_sequence = '>testseq\nSEQSEQSEQSEQ\n'
        rv = self.app.post('/', data={'output_type': 'predict_and_align',
                                      'sequence': test_sequence,
                                      'submit_job': 'Submit'},
                           follow_redirects=True)
        eq_(rv.status_code, 200)
        assert 'Job status' in rv.data
        mock_call1.assert_called_once_with(test_sequence, -5, -1, -1, 10,
                                           3, 3, [], False)

        rv = self.app.post('/', data={'output_type': 'predict',
                                      'sequence': test_sequence,
                                      'submit_job': 'Submit'},
                           follow_redirects=True)
        eq_(rv.status_code, 200)
        assert 'Job status' in rv.data
        mock_call2.assert_called_once_with(test_sequence, [], False)

    def test_methods(self):
        rv = self.app.get('/methods',
                          follow_redirects=True)
        assert 'Methods' in rv.data

    def test_help(self):
        rv = self.app.get('/help',
                          follow_redirects=True)
        assert 'Help' in rv.data

    def test_download(self):
        rv = self.app.post('/download',
                           data={'prediction': 'test_prediction'},
                           follow_redirects=True)
        eq_(rv.data, 'test_prediction')

    def test_download_alignment(self):
        rv = self.app.post('/download_alignment',
                           data={'alignment': 'test_alignment'},
                           follow_redirects=True)
        eq_(rv.data, 'test_alignment')
