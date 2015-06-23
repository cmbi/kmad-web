import logging


from kmad_web.services import txtproc, files


_log = logging.getLogger(__name__)


class KmanStrategyFactory(object):
    @classmethod
    def create(cls, output_type):
        if output_type == 'predict':
            return PredictStrategy(output_type)
        elif output_type in ['predict_and_align', 'hope']:
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

    def __call__(self, fasta_seq, single_fasta_filename, multi_fasta_filename,
                 prediction_methods, multi_seq_input):
        from celery import chain, group
        from kmad_web.tasks import (query_d2p2, run_single_predictor,
                                    postprocess, get_seq, run_blast)

        conffilename = ""
        tasks_to_run = [get_seq.s(fasta_seq)]
        for pred_name in prediction_methods:
            tasks_to_run += [run_single_predictor.s(single_fasta_filename,
                                                    pred_name)]
        workflow = chain(query_d2p2.s(single_fasta_filename, self.output_type,
                                      multi_seq_input),
                         group(tasks_to_run),
                         postprocess.s(single_fasta_filename,
                                       multi_fasta_filename,
                                       conffilename, self.output_type))
        return workflow


class PredictAndAlignStrategy(object):
    def __init__(self, output_type):
        self.output_type = output_type

    def __call__(self, fasta_seq, single_fasta_filename, multi_fasta_filename,
                 gap_opening_penalty, gap_extension_penalty,
                 end_gap_penalty, ptm_score, domain_score, motif_score,
                 prediction_methods, multi_seq_input, usr_features,
                 first_seq_gapped):
        from kmad_web.tasks import (analyze_mutation, query_d2p2, align,
                                    run_single_predictor, run_blast,
                                    postprocess, get_seq)
        from celery import chain, group

        usr_features = txtproc.remove_empty(usr_features)
        if usr_features:
            conffilename = files.write_conf_file(usr_features)
        else:
            conffilename = ""

        tasks_to_run = [get_seq.s(fasta_seq)]
        for pred_name in prediction_methods:
            tasks_to_run += [run_single_predictor.s(single_fasta_filename,
                                                    pred_name)]
        tasks_to_run += [align.s(multi_fasta_filename, gap_opening_penalty,
                                 gap_extension_penalty, end_gap_penalty,
                                 ptm_score, domain_score, motif_score,
                                 multi_seq_input, conffilename,
                                 self.output_type,
                                 first_seq_gapped)]

        workflow = chain(query_d2p2.s(single_fasta_filename, self.output_type,
                                      multi_seq_input),
                         group(tasks_to_run),
                         postprocess.s(single_fasta_filename,
                                       multi_fasta_filename,
                                       conffilename, self.output_type))

        return workflow


class AlignStrategy(object):
    def __init__(self, output_type):
        self.output_type = output_type

    def __call__(self, fasta_seq, single_fasta_filename, multi_fasta_filename,
                 gap_opening_penalty, gap_extension_penalty,
                 end_gap_penalty, ptm_score, domain_score, motif_score,
                 multi_seq_input, usr_features, output_type, first_seq_gapped):
        from kmad_web.tasks import (query_d2p2, align, run_blast,
                                    postprocess, get_seq)
        from celery import chain, group

        usr_features = txtproc.remove_empty(usr_features)
        if usr_features:
            conffilename = files.write_conf_file(usr_features)
        else:
            conffilename = ""

        tasks_to_run = [get_seq.s(fasta_seq),
                        align.s(multi_fasta_filename, gap_opening_penalty,
                                gap_extension_penalty, end_gap_penalty,
                                ptm_score, domain_score, motif_score,
                                multi_seq_input, conffilename, output_type,
                                first_seq_gapped)]
        workflow = chain(query_d2p2.s(single_fasta_filename, self.output_type,
                                      multi_seq_input),
                         group(tasks_to_run),
                         postprocess.s(single_fasta_filename,
                                       multi_fasta_filename,
                                       conffilename, self.output_type))
        return workflow


class AnnotateStrategy(object):
    def __init__(self, output_type):
        self.output_type = output_type

    def __call__(self, fasta_seq, single_fasta_filename, multi_fasta_filename):
        from kmad_web.tasks import (query_d2p2, annotate, run_blast,
                                    postprocess, get_seq)
        from celery import chain, group
        fasta_seq = txtproc.process_fasta(fasta_seq)

        tasks_to_run = [get_seq.s(fasta_seq),
                        annotate.s(multi_fasta_filename)]
        workflow = chain(query_d2p2.s(single_fasta_filename, self.output_type,
                                      True),
                         group(tasks_to_run),
                         postprocess.s(single_fasta_filename,
                                       multi_fasta_filename,
                                       "dummyname", self.output_type))
        return workflow
