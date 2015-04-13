import ast
import inspect
import logging
import re
import StringIO

from flask import Blueprint, render_template, request, send_file
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


@bp.route('/download_api_example', methods=['GET', 'POST'])
def download_api_example():
    with open("kmad_web/frontend/static/files/api_example.py") as a:
            api_example = a.read()
    strIO = StringIO.StringIO()
    strIO.write(api_example)
    strIO.seek(0)
    return send_file(strIO,
                     attachment_filename="kmad_api.py",
                     as_attachment=True)
