import logging
import StringIO

from flask import abort
from flask import (Blueprint, render_template,
                   request, redirect, url_for, send_file)

from kmad_web.services import txtproc, fieldlist_helper
from kmad_web.frontend.dashboard.forms import KmanForm
from kmad_web.services.kmad import KmanStrategyFactory


_log = logging.getLogger(__name__)

bp = Blueprint('dashboard', __name__)


@bp.route("/", methods=['POST', 'GET'])
def index():
    form = KmanForm()
    if (form.submit_job.data and form.validate_on_submit()
            and form.sequence.data and form.output_type.data
            and form.gap_open_p.data and form.gap_ext_p.data
            and form.end_gap_p.data and form.ptm_score.data
            and form.domain_score.data and form.motif_score.data
            and form.first_seq_gapped):
        _log.debug("validation")
        seq_data = form.sequence.data.encode('ascii', errors='ignore')
        strategy = KmanStrategyFactory.create(form.output_type.data)
        _log.debug("Using '{}'".format(strategy.__class__.__name__))
        multi_seq_input = txtproc.check_if_multi(seq_data)  # bool
        if form.output_type.data == "predict":
            job = strategy(seq_data, form.prediction_method.data,
                           multi_seq_input)()
            celery_id = job.id
            _log.debug(form.prediction_method.data)
        elif (form.output_type.data == 'align'
              or form.output_type.data == 'refine'):
            job = strategy(seq_data, form.gap_open_p.data,
                           form.gap_ext_p.data, form.end_gap_p.data,
                           form.ptm_score.data, form.domain_score.data,
                           form.motif_score.data, multi_seq_input,
                           form.usr_features.data, form.output_type.data,
                           form.first_seq_gapped.data)()
            celery_id = job.id
            _log.debug("UsrFeatures: {}".format(form.usr_features.data))
        elif form.output_type.data == 'annotate':
            job = strategy(seq_data)()
            celery_id = job.id
        elif form.output_type.data == 'predict_and_align':
            job = strategy(seq_data, form.gap_open_p.data,
                           form.gap_ext_p.data, form.end_gap_p.data,
                           form.ptm_score.data, form.domain_score.data,
                           form.motif_score.data,
                           form.prediction_method.data, multi_seq_input,
                           form.usr_features.data,
                           form.first_seq_gapped.data)()
            celery_id = job.id
            # IDEA: Could have the strategies (AlignStrategy and
            # PredictStrategy) return the celery workflow (without running it).
            # The workflow would be run here. For this specific elif block,
            # you'd first chain the workflows together.
        elif form.output_type.data == 'hope':
            # 0. Blast
            # 0.1 Filter Blast result
            # 2. Call PredictAndAlign
            # 4. Run workflows in a chain
            pass
        else:
            abort(500, description='Unknown output type')
        _log.info("Job has id '{}'".format(celery_id))
        _log.info("Redirecting to output page")
        return redirect(url_for('dashboard.output',
                                output_type=form.output_type.data,
                                celery_id=celery_id))
    elif form.add_feature.data:
        form.usr_features.append_entry()
    trash_it_data = [i['trash_it'] for i in form.usr_features.data]
    if any(trash_it_data):
        del_index = trash_it_data.index(True)
        fieldlist_helper.delete(form.usr_features, del_index)
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


@bp.route('/examples/<filename>', methods=['GET'])
def alignment_example(filename):
    return render_template('dashboard/examples/{}.html'.format(filename))


@bp.route('/methods', methods=['GET'])
def methods():
    return render_template('dashboard/methods.html')


@bp.route('/about', methods=['GET'])
def about():
    return render_template('dashboard/about.html')


@bp.route('/standalone', methods=['GET'])
def standalone():
    return render_template('dashboard/standalone.html')


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
                     attachment_filename="kmad_alignment.txt",
                     as_attachment=True)
