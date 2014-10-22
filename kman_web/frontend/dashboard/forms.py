import re

from flask_wtf import Form
from wtforms.fields import SelectField, TextAreaField
from wtforms.validators import Regexp

from kman_web.services.files import get_calculated_results


class KmanForm(Form):
    sequence = TextAreaField(u'sequence')
    output_type = SelectField(u'Action', choices=[('predict','predict disorder'), ('predict_and_align','predict and align')])


