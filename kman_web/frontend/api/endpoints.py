import inspect
import logging
import re

from flask import Blueprint, render_template, request
from flask.json import jsonify

from kman_web.services.kman import KmanStrategyFactory


_log = logging.getLogger(__name__)

bp = Blueprint('kman', __name__, url_prefix='/api')


@bp.route('/create/<output_type>/', methods=['POST'])
def create_kman(output_type):
    """
    :param output_type: Either 'predict', 'predict_and_align'.
    :return: The id of the job.

    """
    strategy = KmanStrategyFactory.create(output_type)
    _log.debug("Using '{}'".format(strategy.__class__.__name__))
    celery_id = strategy(request.form['data'])

    _log.info("Task created with id '{}'".format(celery_id))
    return jsonify({'id': celery_id}), 202


@bp.route('/status/<output_type>/<id>/', methods=['GET'])
def get_kman_status(output_type, id):
    """
    Get the status of a previous job submission.
    :param output_type: Either 'predict', 'predict_and_align'.
    :param id: The id returned by a call to the create method.
    :return: Either PENDING, STARTED, SUCCESS, FAILURE, RETRY, or REVOKED.
    """
    from kman_web.tasks import get_task
    task = get_task(output_type)
    async_result = task.AsyncResult(id)

    response = {'status': async_result.status}
    if async_result.failed():
        response.update({'message': async_result.traceback})
    return jsonify(response)


@bp.route('/result/<output_type>/<id>/', methods=['GET'])
def get_kman_result(output_type, id):
    """
    Get the result of a previous job submission.

    :param output_type: Either 'predict', 'predict_and_align'.
    :param id: The id returned by a call to the create method.
    :return: The output of the job. If the job status is not SUCCESS, this
             method returns an error.
    """
    from kman_web.tasks import get_task
    task = get_task(output_type)
    _log.debug("task is {}".format(task.__name__))
    result = task.AsyncResult(id).get()
    if output_type == "predict_and_align":
        response = {'result': {'prediction': result[0:-1], 'alignment': {'raw': result[-1][0],'processed':result[-1][1]}}}
    elif output_type == "predict":
        response = {'result': {'prediction': result}}
    return jsonify(response)


@bp.route('/', methods=['GET'])
def api_doc():
    fs = [create_kman,
          get_kman_status,
          get_kman_result]
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
def api_example():
    return render_template('api/example.html')
