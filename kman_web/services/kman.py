import logging
import tempfile


from kman_web.services import txtproc


_log = logging.getLogger(__name__)


class KmanStrategyFactory(object):
    @classmethod
    def create(cls, output_type):
        if output_type == 'predict':
            return PredictStrategy(output_type)
        elif output_type == 'predict_and_align':
            return PredictAndAlignStrategy(output_type)
        elif output_type == 'align':
            return AlignStrategy(output_type)
        else:
            raise ValueError("Unexpected output type '{}'".format(output_type))


class PredictStrategy(object):
    def __init__(self, output_type):
        self.output_type = output_type

    def __call__(self, fasta_seq, prediction_methods):
        from kman_web.tasks import query_d2p2
        from celery import chain, group
        from kman_web.tasks import run_single_predictor, postprocess, get_seq
        tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
        fasta_seq = txtproc.process_fasta(fasta_seq)
        _log.debug("Created tmp file '{}'".format(tmp_file.name))
        with tmp_file as f:
            _log.debug("Writing data to '{}'".format(tmp_file.name))
            f.write(fasta_seq)

        multi_seq_input = txtproc.check_if_multi(fasta_seq)
        tasks_to_run = [get_seq.s(fasta_seq)]
        for pred_name in prediction_methods:
            tasks_to_run += [run_single_predictor.s(tmp_file.name, pred_name,
                                                    multi_seq_input)]
        job = chain(query_d2p2.s(tmp_file.name, self.output_type,
                                 multi_seq_input),
                    group(tasks_to_run),
                    postprocess.s(tmp_file.name, self.output_type))()
        task_id = job.id

        return task_id


class PredictAndAlignStrategy(object):
    def __init__(self, output_type):
        self.output_type = output_type

    def __call__(self, fasta_seq, gap_opening_penalty, gap_extension_penalty,
                 end_gap_penalty, ptm_score, domain_score, motif_score,
                 prediction_methods, multi_seq_input):
        from kman_web.tasks import (query_d2p2, align,
                                    run_single_predictor, postprocess, get_seq)
        from celery import chain, group
        tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
        fasta_seq = txtproc.process_fasta(fasta_seq)
        _log.debug("Created tmp file '{}'".format(tmp_file.name))
        _log.debug("Chosen prediction method(s): {}".format(prediction_methods))
        with tmp_file as f:
            _log.debug("Writing data to '{}'".format(tmp_file.name))
            f.write(fasta_seq)

        tasks_to_run = [get_seq.s(fasta_seq)]
        multi_seq_input = txtproc.check_if_multi(fasta_seq)
        for pred_name in prediction_methods:
            tasks_to_run += [run_single_predictor.s(tmp_file.name, pred_name,
                                                    multi_seq_input)]
        tasks_to_run += [align.s(tmp_file.name, gap_opening_penalty,
                                 gap_extension_penalty, end_gap_penalty,
                                 ptm_score, domain_score, motif_score,
                                 multi_seq_input)]
        job = chain(query_d2p2.s(tmp_file.name, self.output_type,
                                 multi_seq_input),
                    group(tasks_to_run),
                    postprocess.s(tmp_file.name, self.output_type))()
        task_id = job.id
        return task_id


class AlignStrategy(object):
    def __init__(self, output_type):
        self.output_type = output_type

    def __call__(self, fasta_seq, gap_opening_penalty, gap_extension_penalty,
                 end_gap_penalty, ptm_score, domain_score, motif_score,
                 multi_seq_input):
        from kman_web.tasks import (query_d2p2, align,
                                    postprocess, get_seq)
        from celery import chain, group
        tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
        fasta_seq = txtproc.process_fasta(fasta_seq)
        _log.debug("Created tmp file '{}'".format(tmp_file.name))
        with tmp_file as f:
            _log.debug("Writing data to '{}'".format(tmp_file.name))
            f.write(fasta_seq)
        multi_seq_input = txtproc.check_if_multi(fasta_seq)
        tasks_to_run = [get_seq.s(fasta_seq),
                        align.s(tmp_file.name, gap_opening_penalty,
                                gap_extension_penalty, end_gap_penalty,
                                ptm_score, domain_score, motif_score,
                                multi_seq_input)]
        job = chain(query_d2p2.s(tmp_file.name, self.output_type,
                                 multi_seq_input),
                    group(tasks_to_run),
                    postprocess.s(tmp_file.name, self.output_type))()
        task_id = job.id
        return task_id
