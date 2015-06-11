import logging
import tempfile


from kmad_web.services import txtproc, files


_log = logging.getLogger(__name__)


class KmanStrategyFactory(object):
    @classmethod
    def create(cls, output_type):
        if output_type == 'predict':
            return PredictStrategy(output_type)
        elif output_type == 'predict_and_align':
            return PredictAndAlignStrategy(output_type)
        elif output_type in ['align', 'refine']:
            return AlignStrategy(output_type)
        elif output_type == "annotate":
            return AnnotateStrategy(output_type)
        else:
            raise ValueError("Unexpected output type '{}'".format(output_type))


class PredictStrategy(object):
    def __init__(self, output_type):
        self.output_type = output_type

    def __call__(self, fasta_seq, prediction_methods, multi_seq_input):
        from celery import chain, group
        from kmad_web.tasks import (query_d2p2, run_single_predictor,
                                    postprocess, get_seq, run_blast)
        _log.debug("Called it")
        tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
        fasta_seq = txtproc.process_fasta(fasta_seq)
        _log.debug("Created tmp file '{}'".format(tmp_file.name))
        with tmp_file as f:
            _log.debug("Writing data to '{}'".format(tmp_file.name))
            f.write(fasta_seq)

        align_fasta_filename = tmp_file.name
        conffilename = ""
        if multi_seq_input:
            single_fasta_filename = files.write_single_fasta(fasta_seq)
        else:
            single_fasta_filename = tmp_file.name
        tasks_to_run = [get_seq.s(fasta_seq)]
        for pred_name in prediction_methods:
            tasks_to_run += [run_single_predictor.s(single_fasta_filename,
                                                    pred_name)]
        workflow = chain(run_blast.si(single_fasta_filename),
                         query_d2p2.si(single_fasta_filename, self.output_type,
                                      multi_seq_input),
                         group(tasks_to_run),
                         postprocess.s(single_fasta_filename,
                                       align_fasta_filename,
                                       conffilename, self.output_type))
        return workflow


class PredictAndAlignStrategy(object):
    def __init__(self, output_type):
        self.output_type = output_type

    def __call__(self, fasta_seq, gap_opening_penalty, gap_extension_penalty,
                 end_gap_penalty, ptm_score, domain_score, motif_score,
                 prediction_methods, multi_seq_input, usr_features,
                 first_seq_gapped):
        from kmad_web.tasks import (query_d2p2, align,
                                    run_single_predictor, run_blast,
                                    postprocess, get_seq)
        from celery import chain, group
        tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
        fasta_seq = txtproc.process_fasta(fasta_seq)
        _log.debug("Created tmp file '{}'".format(tmp_file.name))
        _log.debug("Chosen prediction method(s): {}".format(prediction_methods))
        with tmp_file as f:
            _log.debug("Writing data to '{}'".format(tmp_file.name))
            f.write(fasta_seq)
        usr_features = txtproc.remove_empty(usr_features)
        if usr_features:
            conffilename = files.write_conf_file(usr_features)
        else:
            conffilename = ""

        align_fasta_filename = tmp_file.name
        if multi_seq_input:
            single_fasta_filename = files.write_single_fasta(fasta_seq)
        else:
            single_fasta_filename = tmp_file.name

        tasks_to_run = [get_seq.s(fasta_seq)]
        output_type = "predict_and_align"
        for pred_name in prediction_methods:
            tasks_to_run += [run_single_predictor.s(single_fasta_filename,
                                                    pred_name)]
        tasks_to_run += [align.s(align_fasta_filename, gap_opening_penalty,
                                 gap_extension_penalty, end_gap_penalty,
                                 ptm_score, domain_score, motif_score,
                                 multi_seq_input, conffilename, output_type,
                                 first_seq_gapped)]
        workflow = chain(run_blast.si(single_fasta_filename),
                         query_d2p2.si(single_fasta_filename, self.output_type,
                                      multi_seq_input),
                         group(tasks_to_run),
                         postprocess.s(single_fasta_filename,
                                       align_fasta_filename,
                                       conffilename, self.output_type))
        return workflow


class AlignStrategy(object):
    def __init__(self, output_type):
        self.output_type = output_type

    def __call__(self, fasta_seq, gap_opening_penalty, gap_extension_penalty,
                 end_gap_penalty, ptm_score, domain_score, motif_score,
                 multi_seq_input, usr_features, output_type, first_seq_gapped):
        from kmad_web.tasks import (query_d2p2, align, run_blast,
                                    postprocess, get_seq)
        from celery import chain, group
        tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
        fasta_seq = txtproc.process_fasta(fasta_seq)
        _log.debug("Created tmp file '{}'".format(tmp_file.name))
        with tmp_file as f:
            _log.debug("Writing data to '{}'".format(tmp_file.name))
            f.write(fasta_seq)
        usr_features = txtproc.remove_empty(usr_features)
        if usr_features:
            conffilename = files.write_conf_file(usr_features)
        else:
            conffilename = ""

        align_fasta_filename = tmp_file.name
        if multi_seq_input:
            single_fasta_filename = files.write_single_fasta(fasta_seq)
        else:
            single_fasta_filename = tmp_file.name

        tasks_to_run = [get_seq.s(fasta_seq),
                        align.s(align_fasta_filename, gap_opening_penalty,
                                gap_extension_penalty, end_gap_penalty,
                                ptm_score, domain_score, motif_score,
                                multi_seq_input, conffilename, output_type,
                                first_seq_gapped)]
        workflow = chain(run_blast.si(single_fasta_filename),
                         query_d2p2.si(single_fasta_filename, self.output_type,
                                      multi_seq_input),
                         group(tasks_to_run),
                         postprocess.s(single_fasta_filename,
                                       align_fasta_filename,
                                       conffilename, self.output_type))
        return workflow


class AnnotateStrategy(object):
    def __init__(self, output_type):
        self.output_type = output_type

    def __call__(self, fasta_seq):
        from kmad_web.tasks import (query_d2p2, annotate, run_blast,
                                    postprocess, get_seq)
        from celery import chain, group
        tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
        fasta_seq = txtproc.process_fasta(fasta_seq)
        _log.debug("Created tmp file '{}'".format(tmp_file.name))
        with tmp_file as f:
            _log.debug("Writing data to '{}'".format(tmp_file.name))
            f.write(fasta_seq)

        multi_fasta_filename = tmp_file.name
        single_fasta_filename = files.write_single_fasta(fasta_seq)
        tasks_to_run = [get_seq.s(fasta_seq),
                        annotate.s(multi_fasta_filename)]
        workflow = chain(run_blast.si(single_fasta_filename),
                         query_d2p2.si(single_fasta_filename, self.output_type,
                                      True),
                         group(tasks_to_run),
                         postprocess.s(single_fasta_filename,
                                       multi_fasta_filename,
                                       "dummyname", self.output_type))
        return workflow
