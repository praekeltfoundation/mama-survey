from copy import copy

from django import template

from survey.models import Questionnaire, EUNutritionQuiz


register = template.Library()


@register.inclusion_tag('survey/inclusion_tags/survey_listing.html',
                        takes_context=True)
def show_survey(context):
    context = copy(context)
    user = context['user']
    if user.is_authenticated():
        profile = user.profile
        if not profile.decline_surveys:
            survey = Questionnaire.objects.questionnaire_for_user(user)
            context.update({
                'survey': survey
            })
    return context


@register.inclusion_tag('survey/inclusion_tags/eu_home_page_quizzes.html',
                        takes_context=True)
def show_EU_nutrition_quizzes(context):
    context = copy(context)
    user = context['user']
    quizzes = EUNutritionQuiz.objects.home_page_quizzes(user)
    if quizzes:
        context.update({
            'eu_quizzes': quizzes
        })
    return context
