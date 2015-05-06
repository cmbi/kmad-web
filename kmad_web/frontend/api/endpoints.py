import ast
import inspect
import logging
import re

from flask import Blueprint, render_template, request
from flask.json import jsonify

from kmad_web.services.kmad import KmanStrategyFactory
from kmad_web.services import txtproc


_log = logging.getLogger(__name__)

bp = Blueprint('kmad', __name__, url_prefix='/api')


@bp.route('/create/<output_type>/', methods=['POST'])
def create_kmad(output_type):
    """
    :param output_type: Either 'predict', 'predict_and_align', 'align'
    or 'refine'
    :return: The id of the job.

    """
    form = request.form
    strategy = KmanStrategyFactory.create(output_type)
    _log.debug("Using '{}'".format(strategy.__class__.__name__))
    multi_seq_input = txtproc.check_if_multi(form['seq_data'])  # bool
    if output_type == "predict":
        methods = form['prediction_methods'].split()
        celery_id = strategy(request.form['seq_data'],
                             methods,
                             multi_seq_input)
    elif output_type in ['align', 'refine']:
        usr_features = []
        celery_id = strategy(form['seq_data'], float(form['gap_open_p']),
                             float(form['gap_ext_p']), float(form['end_gap_p']),
                             float(form['ptm_score']),
                             float(form['domain_score']),
                             float(form['motif_score']), multi_seq_input,
                             usr_features, form['output_type'],
                             ast.literal_eval(form['first_seq_gapped']))
    elif output_type == 'annotate':
        celery_id = strategy(form['seq_data'])
    else:
        methods = form['prediction_methods'].split()
        usr_features = []
        celery_id = strategy(form['seq_data'], float(form['gap_open_p']),
                             float(form['gap_ext_p']), float(form['end_gap_p']),
                             float(form['ptm_score']),
                             float(form['domain_score']),
                             float(form['motif_score']), methods,
                             multi_seq_input, usr_features,
                             ast.literal_eval(form['first_seq_gapped']))

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
    _log.debug("task is {}".format(task.__name__))
    result = task.AsyncResult(id).get()
    if output_type == "predict_and_align":
        response = {'result': {'prediction': result[0:-1],
                               'feature_codemap': result[-1][3],
                               'alignment': {'raw': result[-1][0],
                                             'processed': result[-1][1],
                                             'encoded': result[-1][2]}}}
    elif output_type == "predict":
        response = {'result': {'prediction': result}}
    elif output_type in ['align', 'refine', 'annotate']:
        response = {'result': {'feature_codemap': result[-1][3],
                               'alignment': {'raw': result[-1][0],
                                             'processed': result[-1][1],
                                             'encoded': result[-1][2]}}}
    return jsonify(response)


@bp.route('/create/', methods=['POST'])
def create():
    import tempfile

    import txtproc
    from kmad_web.tasks import (query_d2p2, align,
                                run_single_predictor, postprocess, get_seq,
                                analyze_mutation)
    from celery import chain, group

    form = request.form
    tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
    fasta_seq = txtproc.process_fasta(form['seq_data'])
    _log.debug("Created tmp file '{}'".format(tmp_file.name))
    with tmp_file as f:
        _log.debug("Writing data to '{}'".format(tmp_file.name))
        f.write(fasta_seq)
    conffilename = ''
    tasks_to_run = [get_seq.s(fasta_seq)]
    output_type = "predict_and_align"
    multi_seq_input = False
    first_seq_gapped = False
    for pred_name in form['prediction_methods'].split():
        tasks_to_run += [run_single_predictor.s(tmp_file.name,
                                                pred_name)]
    tasks_to_run += [align.s(tmp_file.name, form['gap_opening_p'],
                             form['gap_ext_p'], form['end_gap_p'],
                             float(form['ptm_score']), float(['domain_score']),
                             float(['motif_score']),
                             multi_seq_input, conffilename, output_type,
                             first_seq_gapped)]
    job = chain(query_d2p2.s(tmp_file.name, output_type,
                             multi_seq_input),
                group(tasks_to_run),
                postprocess.s(tmp_file.name, 'dummy_filename',
                              conffilename, output_type),
                analyze_mutation.s(int(form['mutation_site']),
                                   form['new_aa'], tmp_file.name))()
    task_id = job.id
    return task_id


@bp.route('/result/<id>/', methods=['GET'])
def get_result(id):

    from kmad_web.tasks import get_task

    task = get_task('hope')

    _log.debug("task is {}".format(task.__name__))
    response = task.AsyncResult(id).get()

    # TODO: Turn result into output...write unit tests! be happy!
    # output = {
    #     'residues': [
    #         {
    #             'position': 1,  # 1-based!
    #             'disordered': 'Y',  # Y = Yes, N = No, M = Maybe
    #             'ptm': [{
    #                 'phosrel': ['certain/putative', 'N', 'description'],
    #                 'glycosylation': ['certain/putative', 'N', 'description']
    #             }],
    #             'motifs': [{
    #                 'motif-a': ['certain/putative', 'M', 'description'],
    #                 'motif-b': ['certain/putative', 'M', 'description']
    #             }],
    #         }
    #     ]
    # }
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
