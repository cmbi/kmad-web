import logging

from flask_wtf import Form
from wtforms import widgets, validators
from wtforms.fields import (FloatField, IntegerField, SelectField,
                            TextAreaField, SelectMultipleField,
                            FieldList, FormField, TextField, SubmitField)
from wtforms.widgets import html_params, HTMLString

logging.basicConfig()
_log = logging.getLogger(__name__)

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


class UsrFeatureEntryForm(Form):
    def validate_positions(form, field):
        if field.data:
            data_list = field.data.replace(' ', '').split(',')
            for i in data_list:
                i_list = i.split('-')
                non_int = not all(e.isdigit() and int(e) > 0 for e in i_list)
                if non_int or len(i_list) not in [1, 2]:
                    _log.debug("item: {}".format(i_list))
                    raise validators.ValidationError('Feature positions need \
                                                      to be listed in a comma \
                                                      separated format, e.g. \
                                                      "1, 2, 15-20" would \
                                                      indicate positions 1, \
                                                      2, and all positions \
                                                      from 15 to 20')

    featname = TextField(u'Feature name', [validators.length(max=10)])
    add_score = IntegerField(u'Add score', [validators.Optional()])
    sequence_number = IntegerField(u'Sequence number', [validators.Optional()])
    positions = TextField(u'Feature positions', [validators.Optional()])
    pattern = TextField(u'Feature pattern(regex)', [validators.Optional()])


class KmanForm(Form):
    def validate_sequence(form, field):
        reading = True
        i = 0
        seq_list = field.data.splitlines()
        if field.data.count('>') < 2:
            if field.data.startswith('>'):
                length = len(''.join(seq_list[1:]))
            else:
                length = len(''.join(seq_list))
            if length < 10:
                raise validators.ValidationError('Sequence should be at least \
                                                  10 amino acids long')
        while reading and i < len(seq_list):
            if (seq_list[i] and not (seq_list[i].startswith('>')
                                     and i < len(seq_list) - 1
                                     and seq_list[i + 1].isalpha())
                            and not seq_list[i].isalpha()):
                raise validators.ValidationError('Sequence should be either in \
                                                  FASTA format or simply a \
                                                  sequence of one-letter amino \
                                                  acid codes')
                reading = False
            i += 1

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
        choices=[('globplot', 'GlobPlot'),
                 ('disopred', 'DISOPRED'),
                 ('spine', 'SPINE-D'),
                 ('psipred', 'PSIPRED'),
                 ('predisorder', 'PreDisorder')],
        default=['globplot'],
        option_widget=widgets.CheckboxInput(),
        widget=MyListWidget(
            html_tag='collist',
            prefix_label=False))
    add_feature = SubmitField()
    remove_feature = SubmitField()
    usr_features = FieldList(FormField(UsrFeatureEntryForm),
                             label="User defined features")

    submit_job = SubmitField("Submit")
