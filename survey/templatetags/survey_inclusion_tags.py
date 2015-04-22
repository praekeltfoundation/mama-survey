from copy import copy

from django import template

from survey.models import Questionnaire, ContentQuiz
from survey.constants import QUESTIONNAIRE_INCOMPLETE, QUESTIONNAIRE_PENDING


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


@register.inclusion_tag('survey/inclusion_tags/content_quizzes.html',
                        takes_context=True)
def show_content_quizzes(context):
    """ Use this template tag to show a content linked quiz outside of the
        context of the content item, e.g. the home page.
    """
    context = copy(context)
    user = context['user']
    quizzes = ContentQuiz.objects.home_page_quizzes(user)
    if quizzes:
        context.update({
            'quizzes': quizzes
        })
    return context


@register.inclusion_tag('survey/inclusion_tags/content_quizzes.html',
                        takes_context=True)
def post_content_quizzes(context, post):
    """ Use this template tag to show the content linked quizzes in the context
        of the Post it is linked to.
    """
    context = copy(context)
    user = context['user']
    result = []
    quizzes = post.post_quiz_set.all()
    for item in quizzes:
        quiz = item.quiz
        if quiz.get_status(user) in (QUESTIONNAIRE_INCOMPLETE,
                                     QUESTIONNAIRE_PENDING):
            result.append(quiz)
    if result:
        context.update({
            'quizzes': result
        })
    return context
