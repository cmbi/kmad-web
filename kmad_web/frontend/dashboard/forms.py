import logging

from flask_wtf import Form
from wtforms import widgets, validators
from wtforms.fields import (FloatField, IntegerField, SelectField,
                            TextAreaField, SelectMultipleField,
                            FieldList, FormField, TextField,
                            SubmitField, RadioField)
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
        self.html_tag = 'ul'
        self.html_end_tag = self.html_tag.split()[0]
        self.prefix_label = prefix_label

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = [u'<%s %s>' % (self.html_tag, html_params(**kwargs))]
        for subfield in field:
            if self.prefix_label:
                html.append(u'<li>%s: %s</li>' % (subfield.label, subfield()))
            else:
                html.append(u'<li>%s %s</li>' % (subfield(), subfield.label))
        html.append(u'</%s>' % self.html_end_tag)
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

    def validate_pattern(form, field):
        if field.data and (form.positions.data or form.sequence_number.data):
            raise validators.ValidationError('Assign feature either by \
                                             position (fill in the \
                                             sequence number and \
                                             positions) OR by pattern - \
                                             not both')

    featname = TextField(u'Feature name', [validators.length(max=10)])
    add_score = FloatField(u'Add score', [validators.Optional()])
    sequence_number = IntegerField(u'Sequence number', [validators.Optional()])
    positions = TextField(u'Feature positions', [validators.Optional()])
    pattern = TextField(u'Feature pattern(regex)', [validators.Optional()])
    trash_it = SubmitField()


def alpha_or_dash(sequence):
    check1 = len(''.join(sequence.split())) > 0
    check2 = all([i.isalpha() or i == '-' for i in sequence])
    return check1 and check2


def check_if_fasta(sequences):
    fasta_header_count = ''.join(sequences).count('>')
    alright = True
    if fasta_header_count > 0:
        # check if first and last are not headers
        alright = (sequences[0].startswith('>')
                   and not sequences[-1].startswith('>')
                   and alpha_or_dash(sequences[-1]))
        if alright:
            for i, lineI in enumerate(sequences[:-1]):
                fasta_header = lineI.startswith('>')
                if fasta_header and not alpha_or_dash(sequences[i + 1]):
                    _log.debug("fasta header and next not alphadash")
                    alright = False
                    break
                elif not fasta_header and not alpha_or_dash(lineI):
                    _log.debug("Current not fasta header and not alpha dash")
                    alright = False
                    break
    elif not alpha_or_dash(''.join(sequences)):
        _log.debug("No fasta headers and not alpha_dash")
        alright = False
    if not alright:
        raise validators.ValidationError('Sequence should be either in \
                                          FASTA format or simply a \
                                          sequence of one-letter amino \
                                          acid codes')


class KmanForm(Form):
    def validate_sequence(form, field):
        i = 0
        seq_list = field.data.splitlines()
        # check seq length
        if field.data.count('>') < 2:
            if field.data.startswith('>'):
                length = len(''.join(seq_list[1:]))
            else:
                length = len(''.join(seq_list))
            if length < 10:
                raise validators.ValidationError('Sequence should be at least \
                                                  10 amino acids long')
        # check format
        check_if_fasta(seq_list)
        # if output type == refine check if multiple sequences are provided
        # and if seq lengths are equal
        if (form.output_type.data == 'annotate'
                or (form.output_type.data == 'refine'
                    and form.alignment_method.data == 'none')):
            if field.data.count('>') < 2:
                raise validators.ValidationError('In the refinement (if no \
                                                 method for initial alignment \
                                                 is specified) and \
                                                 annotation modes \
                                                 the input should \
                                                 be a multiple \
                                                 sequence alignment in FASTA \
                                                 format')
            else:
                tmp_seq = []
                for i in field.data.splitlines():
                    if i.startswith('>'):
                        tmp_seq.append("")
                    else:
                        tmp_seq[-1] += i
                if any([len(i) != len(tmp_seq[0]) for i in tmp_seq]):
                    _log.debug("Sequences: {}".format(tmp_seq))
                    raise validators.ValidationError('Sequences have different \
                                                     lengths - in the \
                                                     refinement and \
                                                     annotations \
                                                     modes  \
                                                     the input should be \
                                                     a multiple \
                                                     sequence alignment in \
                                                     FASTA format (unless you \
                                                     specify  a method for \
                                                     preliminary alignment - \
                                                     then the provided input \
                                                     should be just plain \
                                                     sequences in FASTA format)')

    def validate_gap_open_p(form, field):
        if field.data >= 0:
            raise validators.ValidationError("gap penalty values \
                                             have to be negative")

    def validate_gap_ext_p(form, field):
        if field.data >= 0:
            raise validators.ValidationError("gap penalty values \
                                             have to be negative")

    def validate_end_gap_p(form, field):
        if field.data >= 0:
            raise validators.ValidationError("gap penalty values \
                                             have to be negative")

    def validate_domain_score(form, field):
        if field.data < 0:
            raise validators.ValidationError("domain, motif, and ptm scores \
                                             cannot be negative")

    def validate_motif_score(form, field):
        if field.data < 0:
            raise validators.ValidationError("domain, motif, and ptm scores \
                                             cannot be negative")

    def validate_ptm_score(form, field):
        if field.data < 0:
            raise validators.ValidationError("domain, motif, and ptm scores \
                                             cannot be negative")

    sequence = TextAreaField(u'sequence')
    output_type = SelectField(u'Action', choices=[('align',
                                                   'align'),
                                                  ('refine',
                                                   'refine alignment'),
                                                  ('predict_and_align',
                                                   'predict and align'),
                                                  ('predict',
                                                   'predict disorder'),
                                                  ('annotate',
                                                   'annotate alignment')])
    gap_open_p = FloatField(u'gap opening penalty', default=-12)
    gap_ext_p = FloatField(u'gap extension penalty', default=-1.2)
    end_gap_p = FloatField(u'end gap penalty', default=-1.2)
    ptm_score = FloatField(u'PTM score', default=10)
    domain_score = FloatField(u'domain score', default=4)
    motif_score = FloatField(u'motif score', default=4)

    first_seq_gapped = RadioField(u'First sequence:',
                                  choices=[('ungapped', 'without gaps'),
                                           ('gapped', 'with gaps')],
                                  default='ungapped')

    alignment_method = RadioField(
        u'Alignment method:',
        choices=[('clustalw', 'ClustalW'),
                 ('clustalo', 'Clustal Omega'),
                 ('t_coffee', 'T-Coffee'),
                 ('muscle', 'MUSCLE'),
                 ('mafft', 'MAFFT'),
                 ('none', 'Provide your own alignment for refinement')],
        default='clustalo')
    prediction_method = SelectMultipleField(
        u'Prediction methods:',
        choices=[('globplot', 'GlobPlot'),
                 ('disopred', 'DISOPRED'),
                 ('spine', 'SPINE-D'),
                 ('iupred', 'IUPred'),
                 ('psipred', 'PSIPRED'),
                 ('predisorder', 'PreDisorder')],
        default=['globplot'],
        option_widget=widgets.CheckboxInput(),
        widget=MyListWidget(
            html_tag='collist',
            prefix_label=False))
    add_feature = SubmitField()
    # remove_feature = SubmitField()
    remove_feature = SubmitField()
    seq_limit = IntegerField(u'max. sequence number', default=35)
    filter_motifs = SelectField(u'motif filtering',
                                choices=[('True',
                                          'filter out motifs in structured regions'),
                                         ('False', 'use all motifs')],
                                default='False')

    usr_features = FieldList(FormField(UsrFeatureEntryForm),
                             label="User defined features")

    submit_job = SubmitField("Submit")
