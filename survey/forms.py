from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import RadioSelect

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
    ('now', _('Yes!')),
    ('later', _('Ask me later.')),
    ('decline', _('Do not ask me again.')),
)


class SurveyChoiceForm(forms.Form):
    """ Choose how to proceed with a survey
    """
    survey_id = forms.Field(widget=forms.HiddenInput)
    proceed_choice = forms.ChoiceField(
        widget=RadioSelect,
        choices=_SURVEY_CHOICES,
        label=_('Would you like to participate?'),
        initial='now')

    as_div = as_div


class SurveyQuestionMixin(object):
    """ Mixin class that provides a method to update the multiple choice
        question choices.
    """
    def update_the_form(self, survey_id, the_question):
        """ Create the options for the question and store some hidden fields to
            keep track of where we are.
        """
        # store the survey id in the form
        self.fields['survey_id'].initial = survey_id

        # set the question id and question field attributes on the form
        self.fields['question_id'].initial = the_question.pk
        self.fields['question'].label = the_question.question_text
        self.fields['question'].choices = [
            (itm.pk, itm.option_text,)
            for itm in the_question.multichoiceoption_set.all()]


class SurveyQuestionForm(SurveyQuestionMixin, forms.Form):
    """ Display the options and capture the answer for one question in the
        survey.
    """
    survey_id = forms.Field(widget=forms.HiddenInput)
    question_id = forms.Field(widget=forms.HiddenInput)
    question = forms.ChoiceField(widget=RadioSelect)

    as_div = as_div
