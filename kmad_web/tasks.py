import json
import logging
import os
import subprocess
import tempfile
import urllib2

from celery import current_app as celery_app

from kmad_web.default_settings import (DISOPRED, GLOBPLOT, IUPRED, IUPRED_DIR,
                                       PREDISORDER, PSIPRED, SPINE,
                                       SPINE_OUTPUT_DIR)

from kmad_web.domain.blast.provider import BlastResultProvider
from kmad_web.domain.disorder_prediction.processor import PredictionProcessor
from kmad_web.domain.sequences.provider import UniprotSequenceProvider
from kmad_web.domain.sequences.annotator import SequencesAnnotator
from kmad_web.domain.sequences.encoder import SequencesEncoder
from kmad_web.domain.sequences.fasta import (parse_fasta_alignment,
                                             sequences2fasta)
from kmad_web.domain.fles import write_fles, parse_fles, fles2fasta
from kmad_web.domain.mutation import Mutation
from kmad_web.domain.updaters.elm import ElmUpdater
from kmad_web.services.alignment import (ClustaloService, ClustalwService,
                                         MafftService, MuscleService,
                                         TcoffeeService)
from kmad_web.domain.features.analysis import ptms as ap
from kmad_web.domain.features.analysis import motifs as am

from kmad_web.default_settings import KMAD, BLAST_DB


_log = logging.getLogger(__name__)


@celery_app.task
def run_single_predictor(fasta_file, pred_name):
    _log.info("Run single predictor: {}".format(pred_name))
    env = {}
    if pred_name == "spine":
        tmp_name = fasta_file.split('/')[-1].split('.')[0]
        out_file = os.path.join(SPINE_OUTPUT_DIR, tmp_name + '.spd')
        tmp_path = '/'.join(fasta_file.split("/")[:-1])
        method = SPINE
        args = [method, tmp_path, tmp_name]
    elif pred_name == "disopred":
        out_file = '.'.join(fasta_file.split('.')[:-1])+".diso"
        method = DISOPRED
        args = [method, fasta_file]
    elif pred_name == "predisorder":
        out_file = '.'.join(fasta_file.split('.')[:-1])+".predisorder"
        method = PREDISORDER
        args = [method, fasta_file, out_file]
    elif pred_name == "psipred":
        out_file = ('.'.join(fasta_file.split('.')[:-1])+".ss2").split('/')[-1]
        method = PSIPRED
        args = [method, fasta_file]
    elif pred_name == 'globplot':
        method = GLOBPLOT
        out_file = '.'.join(fasta_file.split('.')[:-1])+".gplot"
        args = [method, '10', '8', '75', '8', '8',
                fasta_file, '>', out_file]
    elif pred_name == 'iupred':
        method = IUPRED
        args = [method, fasta_file, 'long']
        env = {"IUPred_PATH": IUPRED_DIR}

    try:
        data = subprocess.check_output(args, env=env)
        _log.info("Ran command: {}".format(
            subprocess.list2cmdline(args)
        ))
    except (subprocess.CalledProcessError, OSError) as e:
        _log.error("Error: {}".format(e))

    if pred_name not in ['globplot', 'iupred']:
        if os.path.exists(out_file):
            with open(out_file) as f:
                data = f.read()
        else:
            raise RuntimeError("Output file {} doesn't exist".format(
                out_file))
    processor = PredictionProcessor()
    data = processor.process_prediction(data, pred_name)
    return {pred_name: data}


@celery_app.task
def process_prediction_results(predictions, fasta_sequence):
    _log.info("Processing prediction results")
    sequence = ''.join(fasta_sequence.splitlines()[1:])
    # predictions are passed here as a list of single key dictionaries
    # or a single dictionary (if only one predictor was used)
    # -> merge into one dictionary
    if type(predictions) is list:
        predictions = {x.keys()[0]: x.values()[0] for x in predictions}
    processor = PredictionProcessor()
    consensus = processor.get_consensus_disorder(predictions)
    predictions['consensus'] = consensus
    predictions['filtered'] = processor.filter_out_short_stretches(consensus)
    return {'prediction': predictions, 'sequence': sequence}


@celery_app.task
def prealign(sequences, alignment_method):
    service_dict = {
        'clustalo': ClustaloService,
        'clustalw': ClustalwService,
        'mafft': MafftService,
        'muscle': MuscleService,
        't_coffee': TcoffeeService
    }
    fasta = sequences2fasta(sequences)

    tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
    with tmp_file as f:
        f.write(fasta)

    alignment_service = service_dict[alignment_method]()
    filename = alignment_service.align(tmp_file.name)
    with open(filename) as a:
        fasta_file = a.read()
    sequences = parse_fasta_alignment(fasta_file)
    return sequences


@celery_app.task
def run_blast(fasta_sequence):
    _log.info("Running blast")
    tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
    with tmp_file as f:
        f.write(fasta_sequence)

    blast = BlastResultProvider(BLAST_DB)
    blast_result = blast.get_result(tmp_file.name)
    exact_hit = blast.get_exact_hit(blast_result)
    return {
        'blast_result': blast_result,
        'exact_hit': {
            'seq_id': exact_hit,
            'found': bool(exact_hit)
        }
    }


@celery_app.task
def get_sequences_from_blast(blast_result):
    sequences = []
    uniprot = UniprotSequenceProvider()
    for s in blast_result['blast_result']:
        sequence = uniprot.get_sequence(s['id'])
        sequences.append(sequence)
    return sequences


@celery_app.task
def create_fles(sequences, aligned_mode=False):
    """
    Create FLES file (input file for KMAD)
    aligned_mode -> gets passed to the encoder, True if you want to encode
    aligned sequences (then each sequences should have an 'aligned' key:
            {'header': '', 'seq': 'SEQ', 'aligned': 'SE--Q'}
        )

    :param sequences: list sequence dictionaries ({'header': '', 'seq': ''})
    :return: filename
    """
    _log.info("Creating a FLES file")
    annotator = SequencesAnnotator()
    annotator.annotate(sequences)
    encoder = SequencesEncoder()
    encoder.encode(sequences, aligned_mode)
    return {
        'fles_path': write_fles(sequences, aligned_mode),
        'sequences': sequences,
        'motif_code_dict': encoder.motif_code_dict,
        'domain_code_dict': encoder.domain_code_dict
    }


@celery_app.task
def annotate(sequences):
    annotator = SequencesAnnotator()
    annotator.annotate(sequences)
    encoder = SequencesEncoder()
    encoder.encode(sequences, aligned_mode=True)
    return {
        'sequences': sequences,
        'motif_code_dict': encoder.motif_code_dict,
        'domain_code_dict': encoder.domain_code_dict
    }


@celery_app.task
def run_kmad(create_fles_result, gop, gep, egp, ptm_score, domain_score,
             motif_score, conf_path=None, gapped=False, full_ungapped=False,
             refine=False):
    """
    Run KMAD on the given fles_filename and return aligned sequences (dict)

    :param fles_path: path to the FLES file (with encoded sequences)
    :param gop: gap opening penalty
    :param gep: gap extension penalty
    :param egp: end gap penalty
    :param ptm_score: feature weight for PTMs
    :param motif_score: feature weight for motifs
    :param domain_score: feature weight for domains
    :param conf_path: path to the configuration file
    :param gapped: True for standard alignment
    :param full_ungapped: indel-free alignment but in a standard alignment
        format (no residues are cut out from the final alignment,
        but in all alignment rounds profile length is equal
        query sequence length)
    """
    _log.info("Running KMAD")
    fles_path = create_fles_result['fles_path']
    sequences = create_fles_result['sequences']
    args = [KMAD, '-i', fles_path, '-o', fles_path, '-g', gop, '-e', gep,
            '-n', egp, '-p', ptm_score, '-m', motif_score, '-d', domain_score,
            '--out-encoded', '-c', '7']
    result_path = fles_path + '_al'
    # additional parameters
    if conf_path:
        args.extend(['--conf', conf_path])
    if refine:
        args.extend(['--refine'])
    if gapped:
        args.extend(['--gapped'])
    elif full_ungapped:
        args.extend(['--full_ungapped'])

    try:
        subprocess.call(args)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(e)
    else:
        return {
            'fles_path': result_path,
            'sequences': sequences,
            'motif_code_dict': create_fles_result['motif_code_dict'],
            'domain_code_dict': create_fles_result['domain_code_dict']
        }


@celery_app.task
def process_kmad_alignment(run_kmad_result):
    _log.info("Processing KMAD result")
    fles_path = run_kmad_result['fles_path']
    sequences = run_kmad_result['sequences']
    codon_length = 7

    if not os.path.exists(fles_path):
        raise RuntimeError(
            "Couldn't find the alignment file: {}".format(fles_path)
        )

    with open(fles_path) as a:
        fles_file = a.read()
    alignment = parse_fles(fles_file)
    fasta_file = fles2fasta(fles_file)

    for s_index, s in enumerate(alignment):
        sequences[s_index]['encoded_aligned'] = s['encoded_seq']
        sequences[s_index]['aligned'] = s['encoded_seq'][::codon_length]
    return {
        'fles_file': fles_file,
        'fasta_file': fasta_file,
        'sequences': sequences,
        'motif_code_dict': run_kmad_result['motif_code_dict'],
        'domain_code_dict': run_kmad_result['domain_code_dict']
    }


@celery_app.task
def analyze_ptms(process_kmad_result, fasta_sequence, position, mutant_aa):
    sequences = process_kmad_result['sequences']
    mutation = Mutation(sequences[0], position, mutant_aa)
    result = ap.analyze_ptms(mutation, sequences)
    return result


@celery_app.task
def analyze_motifs(process_kmad_result, fasta_sequence, position, mutant_aa):
    sequences = process_kmad_result['sequences']
    mutation = Mutation(sequences[0], position, mutant_aa)
    result = am.analyze_motifs(mutation, sequences)
    return result


@celery_app.task
def query_d2p2(blast_result):
    _log.info("Running query_d2p2")
    data = []
    try:
        if blast_result['exact_hit']['found']:
            seq_id = blast_result['exact_hit']['seq_id']
            data = 'seqids=["%s"]' % seq_id
            request = urllib2.Request('http://d2p2.pro/api/seqid', data)
            response = json.loads(urllib2.urlopen(request).read())
            if response[seq_id]:
                prediction = \
                    response[seq_id][0][2]['disorder']['consensus']
                processor = PredictionProcessor()
                data = processor.process_prediction(prediction, 'd2p2')
    except urllib2.HTTPError and urllib2.URLError:
        _log.debug("D2P2 HTTP/URL Error")
    if data:
        return {'d2p2': data}
    else:
        return None


@celery_app.task
def combine_alignment_and_prediction(results):
    """
    :return: {'prediction': [0, 1, 2],
              'sequence': 'SEQ',
              'fles_file': '>1\nSAAAA...',
              'fasta_file': '>1\nSEQ..'
              'sequences': [],
              'motif_code_dict': {}
              'domain_code_dict': {}
              }
    """
    _log.info("Combining alignment and prediction results")
    combined = results[1]
    combined.update(results[0])
    return combined


@celery_app.task
def update_elmdb(output_filename):
    elm = ElmUpdater()
    elm.update()


def get_task(output_type):
    """
    Get the task for the given output_type.

    If the output_type is not allowed, a ValueError is raised.
    """
    _log.info("Getting task for output '{}'".format(output_type))
    if output_type in ['align', 'refine']:
        task = process_kmad_alignment
    elif output_type == 'predict_and_align':
        task = combine_alignment_and_prediction
    elif output_type == 'ptms':
        task = analyze_ptms
    elif output_type == 'motifs':
        task = analyze_motifs
    elif output_type == 'predict':
        task = process_prediction_results
    else:
        raise ValueError("Unexpected output_type '{}'".format(output_type))

    _log.debug("Got task '{}'".format(task.__name__))
    return task
