import ast
import inspect
import logging
import re

from celery import chain, group

from flask import Blueprint, render_template, request
from flask.json import jsonify

from kmad_web.services.kmad import (PredictStrategy, AlignStrategy)
from kmad_web.services import files


_log = logging.getLogger(__name__)

bp = Blueprint('kmad', __name__, url_prefix='/api')


@bp.route('/create/<output_type>/', methods=['POST'])
def create_kmad(output_type):
    """
    :param output_type: Either 'predict', 'predict_and_align', 'align',
     'refine' or 'hope'
    :return: The id of the job.

    """
    form = request.form
    if output_type == "predict":
        methods = form['prediction_methods'].split()
        strategy = PredictStrategy(form['seq_data'], methods)
        celery_id = strategy()
    elif output_type in ['align', 'refine']:
        usr_features = []
        strategy = AlignStrategy(
            form['seq_data'], str(form['gop']), str(form['gep']),
            str(form['egp']), str(form['ptm_score']), str(form['domain_score']),
            str(form['motif_score']), ast.literal_eval(form['gapped']),
            usr_features
        )
        celery_id = strategy()
    elif output_type == 'annotate':
        workflow = strategy(form['seq_data'], single_fasta_filename,
                            multi_fasta_filename)
        job = chain(run_blast.s(single_fasta_filename, form['seq_limit']),
                    workflow)()
        celery_id = job.id
    elif output_type == 'predict_and_align':
        methods = form['prediction_methods'].split()
        usr_features = []
        workflow = strategy(form['seq_data'], single_fasta_filename,
                            multi_fasta_filename,
                            float(form['gap_open_p']),
                            float(form['gap_ext_p']), float(form['end_gap_p']),
                            float(form['ptm_score']),
                            float(form['domain_score']),
                            float(form['motif_score']), methods,
                            multi_seq_input, usr_features,
                            ast.literal_eval(form['first_seq_gapped']),
                            form['alignment_method'],
                            ast.literal_eval(form['filter_motifs']))
        job = chain(run_blast.s(single_fasta_filename, form['seq_limit']),
                    workflow)()

        celery_id = job.id
    elif output_type == 'hope':
        methods = ['globplot']
        usr_features = []
        gap_open_p = -12
        end_gap_p = -1.2
        gap_ext_p = -1.2
        ptm_score = 12
        motif_score = 3
        domain_score = 3
        first_seq_gapped = True

        from kmad_web.tasks import (align, analyze_mutation, get_seq,
                                    postprocess, query_d2p2,
                                    run_single_predictor,
                                    stupid_task)
        conffilename = ""

        tasks_to_run = [get_seq.s(form['seq_data'])]
        # output_type = "predict_and_align"
        for pred_name in methods:
            tasks_to_run += [run_single_predictor.s(single_fasta_filename,
                                                    pred_name)]
        tasks_to_run += [align.s(multi_fasta_filename, gap_open_p,
                                 gap_ext_p, end_gap_p,
                                 ptm_score, domain_score, motif_score,
                                 multi_seq_input, conffilename,
                                 output_type,
                                 first_seq_gapped)]

        # TODO: stupid task is a VERY WRONG temporary solution
        # without celery gives back the result of the postprocess task instead
        # of analyze-mutation
        workflow = chain(run_blast.s(single_fasta_filename, form['seq_limit']),
                         filter_blast.s(),
                         query_d2p2.s(single_fasta_filename, output_type,
                                      multi_seq_input),
                         group(tasks_to_run),
                         postprocess.s(single_fasta_filename,
                                       multi_fasta_filename,
                                       conffilename, output_type),
                         stupid_task.s(),
                         analyze_mutation.s(int(form['mutation_site']),
                                            form['new_aa'],
                                            single_fasta_filename))

        job = workflow()

        celery_id = job.id

    _log.info("Task created with id '{}'".format(celery_id))
    return jsonify({'id': celery_id}), 202


@bp.route('/status/<output_type>/<id>/', methods=['GET'])
def get_kmad_status(output_type, id):
    """
    Get the status of a previous job submission.
    :param output_type: Either 'predict', 'predict_and_align', 'align'
    or 'refine'
    :param id: The id returned by a call to the create method.
    :return: Either PENDING, STARTED, SUCCESS, FAILURE, RETRY, or REVOKED.
    """
    from kmad_web.tasks import get_task
    task = get_task(output_type)
    async_result = task.AsyncResult(id)

    response = {'status': async_result.status}
    if async_result.failed():
        response.update({'message': async_result.traceback})
    return jsonify(response)


@bp.route('/result/<output_type>/<id>/', methods=['GET'])
def get_kmad_result(output_type, id):
    """
    Get the result of a previous job submission.

    :param output_type: Either 'predict', 'predict_and_align', 'align'
    or 'refine'
    :param id: The id returned by a call to the create method.
    :return: The output of the job. If the job status is not SUCCESS, this
             method returns an error.
    """

    from kmad_web.tasks import get_task

    task = get_task(output_type)
    result = task.AsyncResult(id).get()
    _log.debug("Result: {}".format(result))
    if output_type in ['predict', 'align']:
        response = {'result': result}
    elif output_type in ['refine', 'annotate']:
        _log.debug("Result: {}".format(result))
        response = {'result': {
            'feature_codemap': result[-1]['alignments'][3],
            'annotated_motifs': result[-1]['annotated_motifs'],
            'alignment': {
                'raw': result[-1]['alignments'][0],
                'processed': result[-1]['alignments'][1],
                'encoded': result[-1]['alignments'][2]}}}
    elif output_type == 'hope':
        response = {'result': result}
    return jsonify(response)


@bp.route('/', methods=['GET'])
def api_docs():
    fs = [create_kmad,
          get_kmad_status,
          get_kmad_result]
    docs = {}
    for f in fs:
        src = inspect.getsourcelines(f)
        m = re.search(r"@bp\.route\('([\w\/<>]*)', methods=\['([A-Z]*)']\)",
                      src[0][0])
        if not m:  # pragma: no cover
            _log.debug("Unable to document function '{}'".format(f))
            continue

        url = m.group(1)
        method = m.group(2)
        docstring = inspect.getdoc(f)
        docs[url] = (method, docstring)
    return render_template('api/docs.html', docs=docs)


@bp.route('/example', methods=['GET'])
def api_example():  # pragma: no cover
    return render_template('api/example.html')
