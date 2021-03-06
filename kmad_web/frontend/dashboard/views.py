import ast
import logging
import StringIO

from flask import abort
from flask import (Blueprint, render_template, request, redirect, url_for,
                   send_file)

from kmad_web.request_helpers import get_ip
from kmad_web.services.helpers import fieldlist
from kmad_web.frontend.dashboard.forms import KmadForm
from kmad_web.services.kmad import (AlignStrategy, AnnotateStrategy,
                                    RefineStrategy, PredictStrategy,
                                    PredictAndAlignStrategy)


_log = logging.getLogger(__name__)

bp = Blueprint('dashboard', __name__)


@bp.route("/", methods=['POST', 'GET'])
def index():
    request_ip = get_ip()
    _log.info("Request for 'index' page from IP %s", request_ip)

    form = KmadForm()
    if (form.submit_job.data and form.validate_on_submit()
            and form.sequence.data and form.output_type.data
            and form.gop.data and form.gep.data and form.egp.data
            and form.ptm_score.data and form.domain_score.data
            and form.motif_score.data and form.gapped.data
            and form.seq_limit.data):
        _log.info("[IP: %s] Submitted job: %s", request_ip,
                  form.output_type.data)
        seq_data = form.sequence.data
        _log.info("Submitted seq data: {}".format(seq_data))
        _log.info("Submitted seq data: {}".format(seq_data.splitlines()))
        if form.output_type.data == "predict":
            strategy = PredictStrategy(seq_data, form.prediction_method.data)
            celery_id = strategy()
        elif form.output_type.data == "align":
            strategy = AlignStrategy(
                seq_data, str(form.gop.data), str(form.gep.data),
                str(form.egp.data), str(form.ptm_score.data),
                str(form.domain_score.data), str(form.motif_score.data),
                ast.literal_eval(form.gapped.data), form.usr_features.data,
                form.seq_limit.data)
            celery_id = strategy()
        elif form.output_type.data == 'annotate':
            strategy = AnnotateStrategy(seq_data)
            celery_id = strategy()
        elif form.output_type.data == 'refine':
            gapped = ast.literal_eval(form.gapped.data)
            gapped = True
            strategy = RefineStrategy(
                seq_data, str(form.gop.data), str(form.gep.data),
                str(form.egp.data), str(form.ptm_score.data),
                str(form.domain_score.data), str(form.motif_score.data),
                gapped, form.usr_features.data,
                form.alignment_method.data, form.seq_limit.data)
            celery_id = strategy()
        elif form.output_type.data == 'predict_and_align':
            strategy = PredictAndAlignStrategy(
                seq_data, form.prediction_method.data, str(form.gop.data),
                str(form.gep.data), str(form.egp.data),
                str(form.ptm_score.data), str(form.domain_score.data),
                str(form.motif_score.data), ast.literal_eval(form.gapped.data),
                form.usr_features.data, form.seq_limit.data)
            celery_id = strategy()
        else:
            abort(500, description='Unknown output type')
        _log.info("Job has id '{}'".format(celery_id))
        _log.info("Redirecting to output page")
        return redirect(url_for('dashboard.output',
                                output_type=form.output_type.data,
                                celery_id=celery_id))
    # usr_features form handling
    elif form.add_feature.data:
        form.usr_features.append_entry()
    trash_it_data = [i['trash_it'] for i in form.usr_features.data]
    if any(trash_it_data):
        del_index = trash_it_data.index(True)
        fieldlist.delete(form.usr_features, del_index)

    request_ip = get_ip()
    _log.info("Rendering 'index' page, IP: %s", request_ip)
    return render_template('dashboard/index.html', form=form)


@bp.route("/output/<output_type>/<celery_id>/", methods=['GET'])
def output(output_type, celery_id):
    request_ip = get_ip()
    _log.info("Rendering 'output' page, IP: %s", request_ip)
    _log.info("output_type: %s", output_type)
    _log.info("celery_id: %s", celery_id)
    return render_template("dashboard/output.html",
                           output_type=output_type,
                           celery_id=celery_id)


@bp.route('/help/', methods=['GET'])
def help():
    request_ip = get_ip()
    _log.info("Rendering 'help' page, IP: %s", request_ip)
    return render_template('dashboard/help.html')


@bp.route('/examples/<filename>/', methods=['GET'])
def alignment_example(filename):
    request_ip = get_ip()
    _log.info("Rendering 'examples' page, IP: %s", request_ip)
    return render_template('dashboard/examples/{}.html'.format(filename))


@bp.route('/disprot_clustal_examples/', methods=['GET'])
def disprot_clustal_examples():
    request_ip = get_ip()
    _log.info("Rendering 'disprot clustal examples' page, IP: %s", request_ip)
    return render_template('dashboard/disprot_clustal_examples.html')


@bp.route('/disprot_tcoffee_examples/', methods=['GET'])
def disprot_tcoffee_examples():
    request_ip = get_ip()
    _log.info("Rendering 'disprot tcoffee examples' page, IP: %s", request_ip)
    return render_template('dashboard/disprot_tcoffee_examples.html')


@bp.route('/reviewer_comments/', methods=['GET'])
def reviewer_comments():
    request_ip = get_ip()
    _log.info("Rendering 'reviewer comments' page, IP: %s", request_ip)
    return render_template('dashboard/reviewer_comments.html')


@bp.route('/methods/', methods=['GET'])
def methods():
    request_ip = get_ip()
    _log.info("Rendering 'methods' page, IP: %s", request_ip)
    return render_template('dashboard/methods.html')


@bp.route('/about/', methods=['GET'])
def about():
    request_ip = get_ip()
    _log.info("Rendering 'about' page, IP: %s", request_ip)
    return render_template('dashboard/about.html')


@bp.route('/standalone/', methods=['GET'])
def standalone():
    request_ip = get_ip()
    _log.info("Rendering 'standalone' page, IP: %s", request_ip)
    return render_template('dashboard/standalone.html')


@bp.route('/additional_information/', methods=['GET'])
def additional_information():
    request_ip = get_ip()
    _log.info("Rendering 'additional_information' page, IP: %s", request_ip)
    return render_template('dashboard/additional_information.html')


@bp.route('/why/', methods=['GET'])
def why():
    request_ip = get_ip()
    _log.info("Rendering 'why' page, IP: %s", request_ip)
    return render_template('dashboard/why.html')


@bp.route('/comparison/', methods=['GET'])
def comparison():
    request_ip = get_ip()
    _log.info("Rendering 'comparison' page, IP: %s", request_ip)
    return render_template('dashboard/comparison.html')


@bp.route('/balibase/', methods=['GET'])
def balibase():
    request_ip = get_ip()
    _log.info("Rendering 'balibase' page, IP: %s", request_ip)
    return render_template('dashboard/balibase.html')


@bp.route('/prefab/', methods=['GET'])
def prefab():
    request_ip = get_ip()
    _log.info("Rendering 'prefab' page, IP: %s", request_ip)
    return render_template('dashboard/prefab.html')


@bp.route('/cram/', methods=['GET'])
def cram():
    request_ip = get_ip()
    _log.info("Rendering 'cram' page, IP: %s", request_ip)
    return render_template('dashboard/cram.html')


@bp.route('/1aiq_1b02/', methods=['GET'])
def yasara_example():
    return render_template('dashboard/yasara_example.html')


@bp.route('/download', methods=['POST'])
def download():
    request_ip = get_ip()
    _log.info("Downloading prediction file, IP: %s", request_ip)
    prediction = str(request.form['prediction'])
    strIO = StringIO.StringIO()
    strIO.write(prediction)
    strIO.seek(0)
    return send_file(strIO,
                     attachment_filename="disorder_prediction.txt",
                     as_attachment=True)


@bp.route('/download_alignment', methods=['POST'])
def download_alignment():
    request_ip = get_ip()
    _log.info("Downloading alignment file, IP: %s", request_ip)
    alignment = str(request.form['alignment'])
    strIO = StringIO.StringIO()
    strIO.write(alignment)
    strIO.seek(0)
    return send_file(strIO,
                     attachment_filename="kmad_alignment.txt",
                     as_attachment=True)
