from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import RadioSelect

# from pml import forms as pml_forms
from django import forms
from jmbo.forms import as_div


_SURVEY_CHOICES = (
    ('now', _('I will complete the survey now!')),
    ('later', _('Please remind me later.')),
    # ('decline', _('I do not wish to take part in surveys.')),
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
