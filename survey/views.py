from django.views.generic.base import View, RedirectView, TemplateView
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse

from survey.models import Questionnaire
from survey.forms import SurveyChoiceForm


class CheckForQuestionnaireView(RedirectView):
    """ Invoke this view to automatically get the survey application to check if
        new questionnaires are available for the logged-in user. If so, redirect
        them to the questionnaire page, else the home page.
        
    """
    url = '/'

    def get_redirect_url(self, **kwargs):
        user = self.request.user
        questionnaire = Questionnaire.objects.questionnaire_for_user(user)
        if questionnaire:
            return reverse('survey:survey_action', args=(questionnaire.pk,))

        return super(CheckForQuestionnaireView,self).get_redirect_url(**kwargs)


class ChooseActionFormView(FormView):
    template_name = "survey/survey_choice.html"
    form_class = SurveyChoiceForm 

    def get(self, request, *args, **kwargs):
        survey_id=kwargs.get('survey_id', None)
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        form.fields['survey_id'].initial = survey_id
        return self.render_to_response(self.get_context_data(
                            form=form, 
                            survey_id=survey_id))

    def get_context_data(self, **kwargs):
        survey_id=kwargs.get('survey_id', None)
        if survey_id:
            survey = Questionnaire.objects.get(pk=survey_id)
            kwargs['survey'] = survey
        return kwargs

    def get_success_url(self):
        survey_id = self.request.POST.get('survey_id', None)
        if survey_id is None:
            return reverse('home')
        choice = self.request.POST.get('proceed_choice', 'decline')
        if choice == 'now':
            return reverse('survey:survey_form', args=(survey_id))
        else:
            return reverse('home')


class SurveyFormView(TemplateView):
    template_name = "survey/survey_form.html"
