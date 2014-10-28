import logging
import StringIO

from flask import Blueprint, render_template, request, redirect, url_for, send_file

from kman_web.frontend.dashboard.forms import KmanForm
from kman_web.services.kman import KmanStrategyFactory
from kman_web.services.txtproc import lists_to_text


_log = logging.getLogger(__name__)

bp = Blueprint('dashboard', __name__)


@bp.route("/", methods=['POST', 'GET'])
def index():
    form = KmanForm()
    if form.validate_on_submit() and form.sequence.data and form.output_type.data:
        data = form.sequence.data.encode('ascii', errors='ignore')
        strategy = KmanStrategyFactory.create(form.output_type.data)
        _log.debug("Using '{}'".format(strategy.__class__.__name__))
        celery_id = strategy(data)
        _log.info("Job has id '{}'".format(celery_id))
        _log.info("Redirecting to output page")
        sth ="sth"
        return redirect(url_for('dashboard.output',
                                output_type=form.output_type.data,
                                celery_id=celery_id))
    _log.info("Rendering index page")
    return render_template('dashboard/index.html', form=form)


@bp.route('/out', methods=['POST'])
def fasta_post():
    # TODO: Use wtforms
    text = request.form['fasta']
    processed_text = str(text)
    _log.debug("posted")
    seq, odd, seq_id  = run_predictions(processed_text)
    ## seq: [[method_name, sequence(string)], ...]
    ## odd: [[method_name, disorder(list of integers)], ...]
    
    html_file = open("kman_web/frontend/static/results_html/"+seq_id+".html", 'w')
    html_out = render_template("output.html", seq=seq, odd=odd) 
    html_file.write(html_out)
    html_file.close()
    
    return html_out


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
    
