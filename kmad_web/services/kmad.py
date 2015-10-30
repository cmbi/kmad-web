import logging
import tempfile


from kmad_web.helpers import txtproc
from kmad_web.services import files
from kmad_web.domain.sequences.fasta import (check_fasta, make_fasta,
                                             parse_fasta)


_log = logging.getLogger(__name__)


class MotifsStrategy(object):
    def __init__(self, sequence, position, mutant_aa):
        if not check_fasta(sequence):
            self._fasta_sequence = make_fasta(sequence)
            self._raw_sequence = sequence
        else:
            self._fasta_sequence = sequence
            self._raw_sequence = parse_fasta(sequence)[0]['seq']
        self._position = position
        self._mutant_aa = mutant_aa
        self._feature_type = 'motifs'

    def __call__(self):
        from celery import chain
        from kmad_web.tasks import (run_blast, get_sequences_from_blast,
                                    create_fles, run_kmad, analyze_mutation,
                                    process_kmad_alignment)
        workflow = chain(
            run_blast.s(self._fasta_sequence),
            get_sequences_from_blast.s(),
            create_fles.s(),
            run_kmad.s(),
            process_kmad_alignment.s(),
            analyze_mutation.s(self._raw_sequence, self._position,
                               self._mutant_aa, self._feature_type)
        )
        job = workflow()
        return job.id


class PtmsStrategy(object):
    def __init__(self, sequence, position, mutant_aa):
        if not check_fasta(sequence):
            self._fasta_sequence = make_fasta(sequence)
        else:
            self._fasta_sequence = sequence
        self._position = position
        self._mutant_aa = mutant_aa
        self._feature_type = 'ptms'

    def __call__(self):
        from celery import chain
        from kmad_web.tasks import (run_blast, get_sequences_from_blast,
                                    create_fles, run_kmad, analyze_mutation,
                                    parse_fles)
        workflow = chain(
            run_blast.s(self._fasta_sequence),
            get_sequences_from_blast.s(),
            create_fles.s(),
            run_kmad.s(),
            parse_fles.s(),
            analyze_mutation.s(self._fasta_sequence, self._position,
                               self._mutant_aa, self._feature_type)
        )
        job = workflow()
        return job.id


class PredictStrategy(object):
    def __init__(self, fasta_sequence, prediction_methods):
        self._fasta_sequence = fasta_sequence
        self._prediction_methods = prediction_methods

    def __call__(self):
        from celery import chain, group
        from kmad_web.tasks import (run_blast, query_d2p2, run_single_predictor,
                                    process_prediction_results)

        tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
        with tmp_file as f:
            f.write(self._fasta_sequence)

        if 'd2p2' in self._prediction_methods:
            prediction_tasks = [
                chain(
                    run_blast.s(self._fasta_sequence),
                    query_d2p2.s()
                )
            ]
        else:
            prediction_tasks = []
        for pred_name in self._prediction_methods:
            if pred_name != 'd2p2':
                prediction_tasks += [run_single_predictor.s(tmp_file.name,
                                                            pred_name)]
        print prediction_tasks
        workflow = chain(
            group(prediction_tasks),
            process_prediction_results.s(self._fasta_sequence)
        )
        job = workflow()
        return job.id


# TODO: change
class AlignStrategy(object):
    def __init__(self, sequence_data, gop, gep, egp, ptm_score,
                 domain_score, motif_score, gapped, usr_features):
        self._fasta = make_fasta(sequence_data)
        self._gop = gop
        self._gep = gep
        self._egp = egp
        self._ptm_score = ptm_score
        self._motif_score = motif_score
        self._domain_score = domain_score
        self._gapped = gapped
        self._usr_features = usr_features
        self._multi_fasta = sequence_data.count('>') > 1

    def __call__(self):

        from kmad_web.tasks import (create_fles, run_kmad, run_blast,
                                    process_kmad_alignment)
        from celery import chain

        config_path = files.write_conf_file(self._usr_features)

        if self._multi_fasta:
            sequences = parse_fasta(self._fasta)
            tasks = [create_fles.s(sequences)]
        else:
            tasks = [run_blast.s(self._fasta),
                     create_fles.s()]
        tasks.extend([
            run_kmad.s(self._gop, self._gep, self._egp, self._ptm_score,
                       self._domain_score, self._motif_score, config_path,
                       self._gapped),
            process_kmad_alignment.s()
        ])
        workflow = chain(tasks)
        job = workflow()
        return job.id


# TODO: change
class AnnotateStrategy(object):
    def __init__(self, output_type):
        self.output_type = output_type

    def __call__(self, fasta_seq, single_fasta_filename, multi_fasta_filename):
        from kmad_web.tasks import (query_d2p2, annotate, postprocess, get_seq)
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
