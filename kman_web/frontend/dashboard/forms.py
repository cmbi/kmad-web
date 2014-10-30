from flask_wtf import Form
from wtforms.fields import SelectField, TextAreaField


class KmanForm(Form):
    sequence = TextAreaField(u'sequence')
    output_type = SelectField(u'Action', choices=[('predict',
                                                   'predict disorder'),
                                                  ('predict_and_align',
                                                   'predict and align')])
