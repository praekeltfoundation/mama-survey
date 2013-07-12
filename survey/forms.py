from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import RadioSelect

# from pml import forms as pml_forms
from django import forms


def as_div(form):
    """This formatter arranges label, widget, help text and error messages by
    using divs.  Apply to custom form classes, or use to monkey patch form
    classes not under our direct control."""
    # Yes, evil but the easiest way to set this property for all forms.
    form.required_css_class = 'required'

    return form._html_output(
        normal_row=u"""
            <div class="field">
                <div %(html_class_attr)s>%(label)s %(errors)s
                    <div class="helptext">%(help_text)s</div>
                    %(field)s
                </div>
            </div>""",
        error_row=u'%s',
        row_ender='</div>',
        help_text_html=u'%s',
        errors_on_separate_row=False
    )


_SURVEY_CHOICES = (
    ('now', _('I will complete the survey now!')),
    ('later', _('Please remind me later.')),
    ('decline', _('I do not wish to take part in surveys.')),
)


class SurveyChoiceForm(forms.Form):
    """ Choose how to proceed with a survey
    """
    survey_id = forms.Field(widget=forms.HiddenInput)
    proceed_choice = forms.ChoiceField(
        widget=RadioSelect,
        choices=_SURVEY_CHOICES,
        label=_('How would you like to proceed?'),
        initial='now')

    as_div = as_div


class SurveyQuestionForm(forms.Form):
    """ Display the options and capture the answer for one question in the
        survey.
    """
    survey_id = forms.Field(widget=forms.HiddenInput)
    question_id = forms.Field(widget=forms.HiddenInput)
    question = forms.ChoiceField(widget=RadioSelect)

    as_div = as_div
