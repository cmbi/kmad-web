from mock import patch

from nose.tools import eq_

from kmad_web.factory import create_app


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

    @patch('kmad_web.services.kmad.PredictStrategy.__call__')
    def test_index_post_predict(self, mock_strategy):
        mock_strategy.call.return_value = 12345
        test_sequence = '>testseq\nSEQSEQSEQSEQ\n'
        rv = self.app.post('/', data={'output_type': 'predict',
                                      'sequence': test_sequence,
                                      'submit_job': 'Submit'},
                           follow_redirects=True)
        eq_(rv.status_code, 200)
        assert 'Job status' in rv.data

    @patch('kmad_web.services.kmad.AlignStrategy.__call__')
    def test_index_post_align(self, mock_strategy):
        mock_strategy.call.return_value = 12345
        test_sequence = '>testseq\nSEQSEQSEQSEQ\n'

        rv = self.app.post('/', data={'output_type': 'align',
                                      'gop': '-1', 'gep': '-1', 'egp': '-1',
                                      'motif_score': '12', 'domain_score': '12',
                                      'ptm_score': 12, 'gapped': 'False',
                                      'usr_features': 'usr_features',
                                      'sequence': test_sequence,
                                      'submit_job': 'Submit',
                                      },
                           follow_redirects=True)
        eq_(rv.status_code, 200)
        assert 'Job status' in rv.data

    @patch('kmad_web.services.kmad.RefineStrategy.__call__')
    def test_index_post_refine(self, mock_strategy):
        mock_strategy.call.return_value = 12345
        test_sequence = '>testseq\nSEQSEQSEQSEQ\n'

        rv = self.app.post('/', data={'output_type': 'refine',
                                      'gop': '-1', 'gep': '-1', 'egp': '-1',
                                      'motif_score': '12', 'domain_score': '12',
                                      'ptm_score': 12, 'gapped': 'False',
                                      'usr_features': 'usr_features',
                                      'sequence': test_sequence,
                                      'submit_job': 'Submit',
                                      'alignment_method': 'clustalo'
                                      },
                           follow_redirects=True)
        eq_(rv.status_code, 200)
        assert 'Job status' in rv.data

    @patch('kmad_web.services.kmad.AnnotateStrategy.__call__')
    def test_index_post_annotate(self, mock_strategy):
        mock_strategy.call.return_value = 12345
        test_sequence = '>testseq\nSEQSEQSEQSEQ\n>testseq2\nSEQSEQSEQSEQ'
        rv = self.app.post('/', data={'output_type': 'annotate',
                                      'sequence': test_sequence,
                                      'submit_job': 'Submit'},
                           follow_redirects=True)
        eq_(rv.status_code, 200)
        assert 'Job status' in rv.data

    @patch('kmad_web.services.kmad.PredictAndAlignStrategy.__call__')
    def test_index_post_predict_and_align(self, mock_strategy):
        mock_strategy.call.return_value = 12345
        test_sequence = '>testseq\nSEQSEQSEQSEQ\n'

        rv = self.app.post('/', data={'output_type': 'predict_and_align',
                                      'sequence': test_sequence,
                                      'submit_job': 'Submit',
                                      },
                           follow_redirects=True)
        eq_(rv.status_code, 200)
        assert 'Job status' in rv.data

    def test_methods(self):
        rv = self.app.get('/methods',
                          follow_redirects=True)
        assert 'Methods' in rv.data

    def test_help(self):
        rv = self.app.get('/help',
                          follow_redirects=True)
        assert 'Help' in rv.data

    def test_cram(self):
        rv = self.app.get('/cram',
                          follow_redirects=True)
        assert 'Crambin' in rv.data

    def test_balibase(self):
        rv = self.app.get('/balibase',
                          follow_redirects=True)
        eq_(rv.status_code, 200)

    def test_yasara_example(self):
        rv = self.app.get('/1aiq_1b02',
                          follow_redirects=True)
        eq_(rv.status_code, 200)

    def test_why(self):
        rv = self.app.get('/why',
                          follow_redirects=True)
        eq_(rv.status_code, 200)

    def test_about(self):
        rv = self.app.get('/about',
                          follow_redirects=True)
        eq_(rv.status_code, 200)

    def test_standalone(self):
        rv = self.app.get('/standalone',
                          follow_redirects=True)
        eq_(rv.status_code, 200)

    def test_disprot_clustal_examples(self):
        rv = self.app.get('/disprot_clustal_examples',
                          follow_redirects=True)
        eq_(rv.status_code, 200)

    def test_reviewer_comments(self):
        rv = self.app.get('/reviewer_comments',
                          follow_redirects=True)
        eq_(rv.status_code, 200)

    def test_disprot_tcoffee_examples(self):
        rv = self.app.get('/disprot_tcoffee_examples',
                          follow_redirects=True)
        eq_(rv.status_code, 200)

    def test_additional_information(self):
        rv = self.app.get('/additional_information',
                          follow_redirects=True)
        eq_(rv.status_code, 200)

    def test_prefab(self):
        rv = self.app.get('/prefab',
                          follow_redirects=True)
        eq_(rv.status_code, 200)

    def test_examples(self):
        rv = self.app.get('/examples/alignment1_1',
                          follow_redirects=True)
        eq_(rv.status_code, 200)

    def test_comparison(self):
        rv = self.app.get('/comparison',
                          follow_redirects=True)
        eq_(rv.status_code, 200)

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
