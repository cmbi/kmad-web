from flask_wtf import Form
from wtforms import widgets
from wtforms.fields import (FloatField, IntegerField, SelectField,
                            TextAreaField, SelectMultipleField)
from wtforms.widgets import html_params, HTMLString


class MyListWidget(object):
    """
    Renders a list of fields as a `ul` or `ol` list.

    This is used for fields which encapsulate many inner fields as subfields.
    The widget will try to iterate the field to get access to the subfields and
    call them to render them.

    If `prefix_label` is set, the subfield's label is printed before the field,
    otherwise afterwards. The latter is useful for iterating radios or
    checkboxes.
    """
    def __init__(self, html_tag='ul', prefix_label=True):
        assert html_tag in ('ol', 'ul', 'collist')
        self.html_tag = 'ul id="listwidget"'
        self.prefix_label = prefix_label

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = [u'<%s %s>' % (self.html_tag, html_params(**kwargs))]
        for subfield in field:
            if self.prefix_label:
                html.append(u'<li>%s: %s</li>' % (subfield.label, subfield()))
            else:
                html.append(u'<li>%s %s</li>' % (subfield(), subfield.label))
        html.append(u'</%s>' % self.html_tag)
        return HTMLString(u''.join(html))


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

    prediction_method = SelectMultipleField(
        u'Prediction methods:',
        choices=[('disopred', 'DISOPRED'),
                 ('spined', 'SPINE-D'),
                 ('psipred', 'PSIPRED'),
                 ('predisorder', 'PreDisorder')],
        default=['disopred', 'spined', 'psipred', 'predisorder'],
        option_widget=widgets.CheckboxInput(),
        widget=MyListWidget(
            html_tag='collist',
            prefix_label=False))
