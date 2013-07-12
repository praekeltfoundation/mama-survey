from django.http import HttpResponseRedirect
from django.views.generic.base import View, RedirectView, TemplateView
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse

from survey.models import Questionnaire, MultiChoiceQuestion, AnswerSheet
from survey.forms import SurveyChoiceForm, SurveyQuestionForm


class CheckForQuestionnaireView(RedirectView):
    """ Invoke this view to automatically get the survey application to check
    if new questionnaires are available for the logged-in user. If so, redirect
    them to the questionnaire page, else the home page.
    """
    url = '/'

    def get_redirect_url(self, **kwargs):
        user = self.request.user
        profile = user.profile
        if not profile.decline_surveys:
            questionnaire = Questionnaire.objects.questionnaire_for_user(user)
            if questionnaire:
                return reverse('survey:survey_action',
                               args=(questionnaire.pk,))

        return super(CheckForQuestionnaireView,
                     self).get_redirect_url(**kwargs)


class ChooseActionFormView(FormView):
    """ Present the 'Now', 'Later', 'Decline' choices to the user for the
        applicable questionnaire.
    """
    template_name = "survey/survey_choice.html"
    form_class = SurveyChoiceForm

    def get(self, request, *args, **kwargs):
        survey_id = kwargs.get('survey_id', None)
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        form.fields['survey_id'].initial = survey_id
        return self.render_to_response(self.get_context_data(
            form=form,
            survey_id=survey_id))

    def get_context_data(self, **kwargs):
        survey_id = kwargs.get('survey_id', None)
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
        elif choice == 'decline':
            user = self.request.user
            profile = user.profile
            profile.decline_surveys = True
            profile.save()

        return reverse('home')


class SurveyFormView(FormView):
    """ Display the next available question in the questionnaire to the user.
        If no more questions, redirect to the 'Thank you' page for the
        applicable questionnaire.
    """
    template_name = "survey/survey_form.html"
    form_class = SurveyQuestionForm

    def get(self, request, *args, **kwargs):
        user = self.request.user
        survey_id = kwargs.get('survey_id', None)

        # find the next question to display
        survey = Questionnaire.objects.get(pk=survey_id)
        next_question = survey.get_next_question_for_user(user)
        if next_question is None:
            return HttpResponseRedirect(reverse('survey:thankyou_page',
                                                args=(survey_id,)))

        # create the form
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        # store the survey id in the form
        form = self._update_the_form(form, survey_id, next_question)

        # display the form
        return self.render_to_response(self.get_context_data(
            form=form,
            survey_id=survey_id))

    def post(self, request, *args, **kwargs):

        # check if the user pressed the 'Exit' button.
        if request.POST.get('submit') == 'Exit':
            return HttpResponseRedirect(reverse('survey:exit_page'))

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        # get the choices for the question field, and the hidden field data.
        survey_id = request.POST.get('survey_id')
        question_id = request.POST.get('question_id')
        question = MultiChoiceQuestion.objects.get(pk=question_id)
        form = self._update_the_form(form, survey_id, question)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def _update_the_form(self, form, survey_id, the_question):
        """ Create the options for the question and store some hidden fields to
            keep track of where we are.
        """
        # store the survey id in the form
        form.fields['survey_id'].initial = survey_id

        # set the question id and question field attributes on the form
        form.fields['question_id'].initial = the_question.pk
        form.fields['question'].label = the_question.question_text
        form.fields['question'].choices = [
            (itm.pk, itm.option_text,)
            for itm in the_question.multichoiceoption_set.all()]
        return form

    def form_invalid(self, form):
        survey_id = form.data['survey_id']
        return self.render_to_response(self.get_context_data(
            form=form,
            survey_id=survey_id))

    def form_valid(self, form):
        survey_id = form.cleaned_data['survey_id']
        user = self.request.user
        survey = Questionnaire.objects.get(pk=survey_id)

        sheet, created = AnswerSheet.objects.get_or_create(
            questionnaire=survey,
            user=user)

        # retrieve the question and answer values
        question_id = form.cleaned_data['question_id']
        question = MultiChoiceQuestion.objects.get(pk=question_id)
        selected_option_id = form.cleaned_data['question']
        answer = question.multichoiceoption_set.get(pk=selected_option_id)

        # create the answer instance
        sheet.multichoiceanswer_set.create(question=question,
                                           chosen_option=answer)

        # redirect to the next question
        return HttpResponseRedirect(self.get_success_url(survey_id))

    def get_success_url(self, survey_id):
        return reverse('survey:survey_form', args=(survey_id,))


class SurveyThankyouView(TemplateView):
    """ Display the 'Thank you' page for the applicagble questionnaire.
    """
    template_name = 'survey/survey_thankyou.html'

    def get_context_data(self, **kwargs):
        survey_id = kwargs['survey_id']
        survey = Questionnaire.objects.get(pk=survey_id)
        kwargs['survey'] = survey
        return {
            'params': kwargs
        }


class SurveyExitView(TemplateView):
    """ Display a page if the user pressed 'Exit' on any of the question pages.
    """
    template_name = 'survey/survey_exit.html'
