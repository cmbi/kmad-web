from flask_wtf import Form
from wtforms.fields import FloatField, SelectField, TextAreaField


class KmanForm(Form):
    sequence = TextAreaField(u'sequence')
    output_type = SelectField(u'Action', choices=[('predict',
                                                   'predict disorder'),
                                                  ('predict_and_align',
                                                   'predict and align'),
                                                  ('align',
                                                   'align')])
    gap_open_p = FloatField(u'Gap opening penalty', default=-5)
    gap_ext_p = FloatField(u'Gap extension penalty', default=-1)
    end_gap_p = FloatField(u'End gap penalty', default=-1)
