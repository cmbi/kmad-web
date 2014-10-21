import logging
import os
import tempfile

from kman_web.services import txtproc


_log = logging.getLogger(__name__)


def getID(seq, tmpname):
    header = seq.split("\n")[0].split("|")
    if len(header) > 1:
        seq_id = header[1]
    else: 
        seq_id = (tmpname.split("/")[-1]).split(".")[0]
    return seq_id


class KmanStrategyFactory(object):
    @classmethod
    def create(cls, output_type):
        if output_type == 'predict':
            return PredictStrategy(output_type)
        elif output_type == 'predict_and_align':
            return PredictAndAlignStrategy(output_type)
        else:
            raise ValueError("Unexpected output type '{}'".format(output_type))


class PredictStrategy(object):
    def __init__(self, output_type):
        self.output_type = output_type

    def __call__(self, fasta_seq):
        from kman_web.tasks import query_d2p2
        from celery import chain, group
        from kman_web.tasks import run_single_predictor, postprocess, get_seq
        tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta",delete=False)
        fasta_seq = txtproc.process_fasta(fasta_seq)
        sequence = fasta_seq.splitlines()[1]
        seq_id = getID(fasta_seq, tmp_file.name)
        _log.debug("Created tmp file '{}'".format(tmp_file.name))
        with tmp_file as f:
            _log.debug("Writing data to '{}'".format(tmp_file.name))
            f.write(fasta_seq)

        methods = ["dummy"]
        tasks_to_run = [get_seq.s(fasta_seq)]
        tasks_to_run += [run_single_predictor.s(tmp_file.name, pred_name, seq_id) for pred_name in methods] 
        job = chain(query_d2p2.s(tmp_file.name), group(tasks_to_run), postprocess.s(tmp_file.name, self.output_type))()
        task_id = job.id

        return task_id


class PredictAndAlignStrategy(object):
    def __init__(self, output_type):
        self.output_type = output_type

    def __call__(self, fasta_seq):
        from kman_web.tasks import query_d2p2, align, run_single_predictor, postprocess, get_seq
        from celery import chain, group
        tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta",delete=False)
        fasta_seq = txtproc.process_fasta(fasta_seq)
        sequence = fasta_seq.splitlines()[1]
        seq_id = getID(fasta_seq, tmp_file.name)
        _log.debug("Created tmp file '{}'".format(tmp_file.name))
        with tmp_file as f:
            _log.debug("Writing data to '{}'".format(tmp_file.name))
            f.write(fasta_seq)


        methods = ["spine", "predisorder", "psipred", "disopred"]
        tasks_to_run = [get_seq.s(fasta_seq)]
        tasks_to_run += [run_single_predictor.s(tmp_file.name, pred_name, seq_id) for pred_name in methods] 
        tasks_to_run += [align.s(tmp_file.name)]
        job = chain(query_d2p2.s(tmp_file.name), group(tasks_to_run), postprocess.s(tmp_file.name, self.output_type))()
        task_id = job.id
        return task_id
