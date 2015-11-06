import ast
import inspect
import logging
import re

from flask import Blueprint, render_template, request
from flask.json import jsonify

from kmad_web.services.kmad import (PredictStrategy, AlignStrategy,
                                    PtmsStrategy, MotifsStrategy)


_log = logging.getLogger(__name__)

bp = Blueprint('kmad', __name__, url_prefix='/api')


@bp.route('/create/<output_type>/', methods=['POST'])
def create_kmad(output_type):
    """
    :param output_type: Either 'predict', 'align',
     'refine', 'ptms' or 'motifs'
    :return: The id of the job.

    """
    form = request.form
    if output_type == "predict":
        methods = form['prediction_methods'].split()
        strategy = PredictStrategy(form['seq_data'], methods)
    elif output_type == 'align':
        usr_features = []
        strategy = AlignStrategy(
            form['seq_data'], str(form['gop']), str(form['gep']),
            str(form['egp']), str(form['ptm_score']), str(form['domain_score']),
            str(form['motif_score']), ast.literal_eval(form['gapped']),
            usr_features
        )
    elif output_type == 'ptms':
        strategy = PtmsStrategy(form['seq_data'], int(form['position']),
                                form['mutant_aa'])
    elif output_type == 'motifs':
        strategy = MotifsStrategy(form['seq_data'], int(form['position']),
                                  form['mutant_aa'])
    celery_id = strategy()
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
