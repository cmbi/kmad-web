from mock import mock_open, patch, PropertyMock
from nose.tools import eq_, ok_, raises

from kmad_web.factory import create_app, create_celery_app


class TestTasks(object):

    @classmethod
    def setup_class(cls):
        flask_app = create_app({'TESTING': True,
                                'CELERY_ALWAYS_EAGER': True
                                })
        cls.celery = create_celery_app(flask_app)

    def test_get_task(self):

        from kmad_web.tasks import (get_task, annotate,
                                    combine_alignment_and_prediction,
                                    process_prediction_results,
                                    process_kmad_alignment, analyze_ptms,
                                    analyze_motifs)

        output_type = 'predict'
        expected = process_prediction_results
        result = get_task(output_type)
        eq_(result, expected)

        output_type = 'align'
        expected = process_kmad_alignment
        result = get_task(output_type)
        eq_(result, expected)

        output_type = 'ptms'
        expected = analyze_ptms
        result = get_task(output_type)
        eq_(result, expected)

        output_type = 'motifs'
        expected = analyze_motifs
        result = get_task(output_type)
        eq_(result, expected)

        output_type = 'annotate'
        expected = annotate
        result = get_task(output_type)
        eq_(result, expected)

        output_type = 'predict_and_align'
        expected = combine_alignment_and_prediction
        result = get_task(output_type)
        eq_(result, expected)

    @raises(ValueError)
    def test_get_value_error(self):
        output_type = 'incorrect_value'

        from kmad_web.tasks import get_task

        get_task(output_type)

    def test_query_d2p2(self):
        from kmad_web.tasks import query_d2p2

        # check: sequence not found in swissprot
        blast_result = {
            'exact_hit': {'found': False}
        }
        expected = None

        result = query_d2p2(blast_result)
        eq_(result, expected)

        # check: sequence found in d2p2
        blast_result = {
            'exact_hit': {'found': True, 'seq_id': 'P10636'}
        }
        result = query_d2p2(blast_result)
        ok_(result)

    @patch('kmad_web.tasks.os.path.exists')
    @patch('kmad_web.tasks.PredictionProcessor.process_prediction')
    @patch('kmad_web.tasks.iupred')
    @patch('kmad_web.tasks.psipred')
    @patch('kmad_web.tasks.disopred')
    @patch('kmad_web.tasks.predisorder')
    @patch('kmad_web.tasks.globplot')
    @patch('kmad_web.tasks.spined')
    def test_run_single_predictor(self, mock_spined, mock_globplot,
                                  mock_predisorder, mock_disopred, mock_psipred,
                                  mock_iupred, mock_process, mock_os):
        fasta = '>1\nSEQSEQ'
        methods = ['psipred', 'predisorder', 'disopred', 'spined', 'globplot',
                   'iupred']

        pred = "prediction"
        mock_disopred.return_value = pred
        mock_psipred.return_value = pred
        mock_iupred.return_value = pred
        mock_predisorder.return_value = pred
        mock_globplot.return_value = pred
        mock_spined.return_value = pred
        mock_process.return_value = pred

        mock_os.return_value = True

        from kmad_web.tasks import run_single_predictor

        for pred_name in methods:
            expected = {pred_name: pred}

            result = run_single_predictor(fasta, pred_name)
            eq_(result, expected)

        result = run_single_predictor(fasta, pred_name)
        eq_(result,  expected)

    def test_process_prediction_results(self):
        fasta_seq = '>1\nSEQSEQ\n'
        predictions_in = [
            {'disopred': [0, 0, 0, 0, 2, 2]},
            {'predisorder': [2, 2, 0, 0, 2, 2]}
        ]

        from kmad_web.tasks import process_prediction_results

        result = process_prediction_results(predictions_in, fasta_seq)
        prediction_text = "ResNo AA consensus filtered disopred predisorder\n" \
                          "1 S 1 1 0 2\n" \
                          "2 E 1 1 0 2\n" \
                          "3 Q 0 0 0 0\n" \
                          "4 S 0 0 0 0\n" \
                          "5 E 2 2 2 2\n" \
                          "6 Q 2 2 2 2"

        expected = {
            'prediction_text': prediction_text,
            'prediction': {
                'disopred': [0, 0, 0, 0, 2, 2],
                'predisorder': [2, 2, 0, 0, 2, 2],
                'consensus': [1, 1, 0, 0, 2, 2],
                'filtered': [1, 1, 0, 0, 2, 2]
            },
            'sequence': 'SEQSEQ'
        }
        eq_(expected, result)

    @patch('kmad_web.tasks.tempfile')
    @patch('kmad_web.tasks.TcoffeeService')
    @patch('kmad_web.tasks.MuscleService')
    @patch('kmad_web.tasks.MafftService')
    @patch('kmad_web.tasks.ClustalwService')
    @patch('kmad_web.tasks.ClustaloService')
    @patch('kmad_web.tasks.open', mock_open(read_data='>1\nSEQSEQ\n'),
           create=True)
    def test_prealign(self, mock_clustalo, mock_clustalw, mock_mafft,
                      mock_muscle, mock_tcoffee, mock_temp):

        from kmad_web.tasks import prealign

        methods = ['clustalo', 'clustalw', 'mafft', 'muscle', 't_coffee']
        sequences = [{'seq': 'SEQSEQ', 'header': '>1'}]
        expected = [{'seq': 'SEQSEQ', 'header': '>1', 'aligned': 'SEQSEQ'}]
        for m in methods:
            result = prealign(sequences, m)
            eq_(expected, result)

    @patch('kmad_web.tasks.tempfile')
    @patch('kmad_web.tasks.BlastResultProvider.get_result')
    @patch('kmad_web.tasks.BlastResultProvider.get_exact_hit')
    def test_run_blast(self, mock_hit, mock_res, mock_tmp):

        from kmad_web.tasks import run_blast

        fasta_seq = '>1\nSEQSEQ\n'

        mock_res.return_value = 'blast_result'
        mock_hit.return_value = 'exact_hit'
        expected = {
            'blast_result': 'blast_result',
            'exact_hit': {
                'seq_id': 'exact_hit',
                'found': True
            }
        }
        eq_(expected, run_blast(fasta_seq))

        mock_hit.return_value = 'exact_hit'
        expected = {
            'blast_result': 'blast_result',
            'exact_hit': {
                'seq_id': 'exact_hit',
                'found': True
            }
        }
        eq_(expected, run_blast(fasta_seq))

    @patch('kmad_web.tasks.UniprotSequenceProvider.get_sequence')
    def test_get_sequences_from_blast(self, mock_provider):
        sequences = ['seq1', 'seq2']
        mock_provider.side_effect = sequences
        blast_result = {'blast_result':
                        [{'id': '1'}, {'id': '2'}]
                        }
        from kmad_web.tasks import get_sequences_from_blast

        eq_(sequences, get_sequences_from_blast(blast_result))

    @patch('kmad_web.tasks.make_fles')
    @patch('kmad_web.tasks.SequencesEncoder')
    @patch('kmad_web.tasks.SequencesAnnotator')
    def test_annotate(self, mock_annotator, mock_encoder, mock_fles):

        from kmad_web.tasks import annotate

        motif_dict = {'motif_aa': 'aa'}
        domain_dict = {'domain_aa': 'aa'}
        fles_file = 'fles_file'
        type(mock_encoder.return_value).motif_code_dict = PropertyMock(
            return_value=motif_dict)
        type(mock_encoder.return_value).domain_code_dict = PropertyMock(
            return_value=domain_dict)
        mock_fles.return_value = fles_file

        sequences = 'sequences'
        expected = {
            'motif_code_dict': {'aa': 'motif_aa'},
            'domain_code_dict': {'aa': 'domain_aa'},
            'sequences': sequences
        }

        eq_(expected, annotate(sequences))

    @patch('kmad_web.tasks.ElmUpdater.update')
    def test_update_elmdb(self, mock_update):
        from kmad_web.tasks import update_elmdb

        update_elmdb()
        mock_update.assert_called_once()

    def test_combine_alignment_and_prediciton(self):
        from kmad_web.tasks import combine_alignment_and_prediction
        task_input = [
            {
                'fles_file': 'test',
                'fasta_file': 'test',
                'sequences': 'test',
                'motif_code_dict': 'test',
                'domain_code_dict': 'test'
            },
            {
                'prediction': 'test',
                'prediction_text': 'test',
                'sequence': 'test'
            }
        ]

        expected = {
            'fles_file': 'test',
            'fasta_file': 'test',
            'sequences': 'test',
            'motif_code_dict': 'test',
            'domain_code_dict': 'test',
            'prediction': 'test',
            'prediction_text': 'test',
            'sequence': 'test',
            'sequences': 'test'
        }
        eq_(expected, combine_alignment_and_prediction(task_input))
