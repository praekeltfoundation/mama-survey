from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required

from survey.views import (CheckForQuestionnaireView, ChooseActionFormView,
                            SurveyFormView)

urlpatterns = patterns('',
    url(
        r'^check-for-survey/',
        login_required(CheckForQuestionnaireView.as_view()),
        name='check_for_survey'
    ),
    url(
        r'^survey-action/(?P<survey_id>\d+)/',
        login_required(ChooseActionFormView.as_view()),
        name='survey_action'
    ),
    url(
        r'^survey/(?P<survey_id>\d+)/',
        login_required(SurveyFormView.as_view()),
        name='survey_form'
    ),
)
