from flask_wtf import Form
from wtforms.fields import FloatField, IntegerField, SelectField, TextAreaField


class KmanForm(Form):
    sequence = TextAreaField(u'sequence')
    output_type = SelectField(u'Action', choices=[('align',
                                                   'align'),
                                                  ('predict_and_align',
                                                   'predict and align'),
                                                  ('predict',
                                                   'predict disorder')])
    gap_open_p = FloatField(u'gap opening penalty', default=-5)
    gap_ext_p = FloatField(u'gap extension penalty', default=-1)
    end_gap_p = FloatField(u'end gap penalty', default=-1)
    ptm_score = IntegerField(u'PTM score', default=10)
    domain_score = IntegerField(u'domain score', default=3)
    motif_score = IntegerField(u'motif score', default=3)
