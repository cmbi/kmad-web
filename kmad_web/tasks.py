import json
import logging
import os
import tempfile
import requests

from celery import current_app as celery_app

from kmad_web.domain.blast.provider import BlastResultProvider
from kmad_web.domain.disorder_prediction.processor import PredictionProcessor
from kmad_web.domain.sequences.provider import UniprotSequenceProvider
from kmad_web.domain.sequences.annotator import SequencesAnnotator
from kmad_web.domain.sequences.encoder import SequencesEncoder
from kmad_web.domain.sequences.fasta import (parse_fasta_alignment,
                                             sequences2fasta)
from kmad_web.domain.fles import make_fles, parse_fles, fles2fasta
from kmad_web.domain.mutation import Mutation
from kmad_web.domain.updaters.elm import ElmUpdater
from kmad_web.services.alignment import (ClustaloService, ClustalwService,
                                         MafftService, MuscleService,
                                         TcoffeeService)
from kmad_web.domain.features.analysis import ptms as ap
from kmad_web.domain.features.analysis import motifs as am
from kmad_web.helpers import invert_dict
from kmad_web.services.iupred import iupred
from kmad_web.services.psipred import psipred
from kmad_web.services.disopred import disopred
from kmad_web.services.predisorder import predisorder
from kmad_web.services.globplot import globplot
from kmad_web.services.spined import spined
from kmad_web.services.kmad_aligner import kmad
from kmad_web.services.types import ServiceError

from kmad_web.default_settings import BLAST_DB, D2P2_URL


_log = logging.getLogger(__name__)


@celery_app.task
def run_single_predictor(fasta_sequence, pred_name):
    _log.info("Run single predictor: {}[task]".format(pred_name))
    data = globals()[pred_name](fasta_sequence)
    processor = PredictionProcessor()
    prediction = processor.process_prediction(data, pred_name)
    return {pred_name: prediction}


@celery_app.task
def process_prediction_results(predictions, fasta_sequence):
    _log.info("Processing prediction results")
    sequence = ''.join(fasta_sequence.splitlines()[1:])
    # predictions are passed here as a list of single key dictionaries
    # or a single dictionary (if only one predictor was used)
    # -> merge into one dictionary
    if type(predictions) is list:
        predictions = filter(None, predictions)
        predictions = {x.keys()[0]: x.values()[0] for x in predictions}
    processor = PredictionProcessor()
    if predictions:
        consensus = processor.get_consensus_disorder(predictions)
        predictions['consensus'] = consensus
        predictions['filtered'] = processor.filter_out_short_stretches(
            consensus)
    prediction_text = processor.make_text(predictions, sequence)
    return {'prediction': predictions, 'sequence': sequence,
            'prediction_text': prediction_text}


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
        try:
            sequence = uniprot.get_sequence(s['id'])
            sequences.append(sequence)
        except ServiceError:
            _log.warning("Couldn't get sequence for id: {}".format(s['id']))
    _log.debug("Got {} sequences".format(len(sequences)))
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
    fles_file = make_fles(sequences, aligned_mode)
    return {
        'fles_file': fles_file,
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
        'motif_code_dict': invert_dict(encoder.motif_code_dict),
        'domain_code_dict': invert_dict(encoder.domain_code_dict)
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
    _log.info("Running KMAD alignment [task]")
    fles_file = create_fles_result['fles_file']
    sequences = create_fles_result['sequences']
    result_path = kmad.align(fles_file, gop, gep, egp, ptm_score, domain_score,
                             motif_score, conf_path, gapped, full_ungapped,
                             refine)
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
        'motif_code_dict': invert_dict(run_kmad_result['motif_code_dict']),
        'domain_code_dict': invert_dict(run_kmad_result['domain_code_dict'])
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
    result = []
    try:
        if blast_result['exact_hit']['found']:
            seq_id = blast_result['exact_hit']['seq_id']
            url = os.path.join(D2P2_URL, '["{}"]'.format(seq_id))
            response = requests.get(url)
            response.raise_for_status()
            res_json = json.loads(response.text)
            if 'error' not in res_json.keys() and res_json[seq_id]:
                prediction = res_json[seq_id][0][2]['disorder']['consensus']
                processor = PredictionProcessor()
                result = processor.process_prediction(prediction, 'd2p2')
            else:
                _log.debug("D2P2 error: {}".format(result))
    except (requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError):
        _log.debug("D2P2 HTTP/URL Error")
    if result:
        return {'d2p2': result}
    else:
        return None


@celery_app.task
def combine_alignment_and_prediction(results):
    """
    :return: {'prediction': [0, 1, 2],
              'prediction_text': prediction_text,
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
def update_elmdb():
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
    elif output_type == 'annotate':
        task = annotate
    elif output_type == 'predict':
        task = process_prediction_results
    else:
        raise ValueError("Unexpected output_type '{}'".format(output_type))

    _log.debug("Got task '{}'".format(task.__name__))
    return task
