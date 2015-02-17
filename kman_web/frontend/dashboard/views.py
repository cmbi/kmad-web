import logging
import StringIO

from flask import (Blueprint, render_template,
                   request, redirect, url_for, send_file)

from kman_web.frontend.dashboard.forms import KmanForm
from kman_web.services.kman import KmanStrategyFactory


_log = logging.getLogger(__name__)

bp = Blueprint('dashboard', __name__)


@bp.route("/", methods=['POST', 'GET'])
def index():
    form = KmanForm()
    if (form.submit_job.data and form.validate_on_submit()
            and form.sequence.data
            and form.output_type.data
            and form.gap_open_p.data
            and form.gap_ext_p.data
            and form.end_gap_p.data
            and form.ptm_score.data
            and form.domain_score.data
            and form.motif_score.data):
        _log.debug("validation")
        data = form.sequence.data.encode('ascii', errors='ignore')
        strategy = KmanStrategyFactory.create(form.output_type.data)
        _log.debug("Using '{}'".format(strategy.__class__.__name__))
        if form.output_type.data == "predict":
            celery_id = strategy(data, form.prediction_method.data)
            _log.debug(form.prediction_method.data)
        elif form.output_type.data == 'align':
            celery_id = strategy(data, form.gap_open_p.data,
                                 form.gap_ext_p.data, form.end_gap_p.data,
                                 form.ptm_score.data, form.domain_score.data,
                                 form.motif_score.data)
            _log.debug("UsrFeatures: {}".format(form.usr_features.data))
        else:
            celery_id = strategy(data, form.gap_open_p.data,
                                 form.gap_ext_p.data, form.end_gap_p.data,
                                 form.ptm_score.data, form.domain_score.data,
                                 form.motif_score.data,
                                 form.prediction_method.data)
        _log.info("Job has id '{}'".format(celery_id))
        _log.info("Redirecting to output page")
        return redirect(url_for('dashboard.output',
                                output_type=form.output_type.data,
                                celery_id=celery_id))
    elif form.add_feature.data:
        form.usr_features.append_entry()
    elif form.remove_feature.data:
        form.usr_features.pop_entry()
    _log.info("Rendering index page")
    return render_template('dashboard/index.html', form=form)


@bp.route("/output/<output_type>/<celery_id>", methods=['GET'])
def output(output_type, celery_id):
    return render_template("dashboard/output.html",
                           output_type=output_type,
                           celery_id=celery_id)


@bp.route('/help', methods=['GET'])
def help():
    return render_template('dashboard/help.html')


@bp.route('/methods', methods=['GET'])
def methods():
    return render_template('dashboard/methods.html')


@bp.route('/download', methods=['POST'])
def download():
    prediction = str(request.form['prediction'])
    strIO = StringIO.StringIO()
    strIO.write(prediction)
    strIO.seek(0)
    return send_file(strIO,
                     attachment_filename="disorder_prediction.txt",
                     as_attachment=True)


@bp.route('/download_alignment', methods=['POST'])
def download_alignment():
    alignment = str(request.form['alignment'])
    strIO = StringIO.StringIO()
    strIO.write(alignment)
    strIO.seek(0)
    return send_file(strIO,
                     attachment_filename="kman_alignment.txt",
                     as_attachment=True)
