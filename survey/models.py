from django.db import models
from django.contrib.auth.models import User


class QuestionnaireManager(models.Manager):
    """ Model manager for questionnaire models. Used mainly to determine if a 
        questionnaire is available for a given user.
    """

    def questionnaire_available_for_user(self, user):
        """ Determine if a questionnaire is available for a given user
        """
        return True


class Questionnaire(models.Model):
    """ Defines an available Questionnaire
    """
    title = models.CharField(max_length=100, blank=False)
    introduction_text = models.TextField(blank=False)
    thank_you_text = models.CharField(blank=False)
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, blank=False)
    active = models.BooleanField(default=False)

    objects = QuestionnaireManager

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ('-date_created',)

    def get_next_question_for_user(self, user):
        """ Retrieve the next unanswered question in the questionnaire
        """

class MultiChoiceQuestion(models.Model):
    """ Defines a multiple choice type question on the questionnaire
    """
    questionnaire = models.ForeignKey(Questionnaire, blank=False)
    question_order = models.PositiveIntegerField(blank=False)
    question_text = models.CharField(max_length=255, blank=False)

    def __unicode__(self):
        return self.question_text

    class Meta:
        ordering = ('question_order',)

    
class MultiChoiceOption(models.Model):
    """ Defines a selectable multiple choice answer option
    """
    question = models.ForeignKey(MultiChoiceQuestion, blank=False)
    option_order = models.PositiveIntegerField(blank=False)
    option_text = models.CharField(max_length=255)
    is_correct_option = models.BooleanField(default=False)

    def __unicode__(self):
        return self.option_text

    class Meta:
        ordering = ('option_order',)


class AnswerSheet(models.Model):
    """ Contains the answers provided by the user in response to the questions
        contained in the questionnaire.
    """
    questionnaire = models.OneToOneField(Questionnaire, blank=False)
    user = models.OneToOneField(User, blank=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_last_updated = models.DateTimeField(auto_now_update=True, blank=True)

    def __unicode__(self):
        return "%s by %s" % (questionnaire.title, user.username)

    class Meta:
        ordering = ('user', 'date_created',)

    def is_complete(self, user):
        """ Determine if a user has completed the questionnaire
        """

class MultiChoiceAnswer(models.Model):
    """ Store the answer option that the user selected
    """
    answer_sheet = models.OneToOneField(AnswerSheet, blank=False)
    question = models.OneToOneField(MultiChoiceQuestion, blank=False)
    chosen_option = models.OneToOneField(MultiChoiceOption, blank=False)

    def __unicode__(self):
        return "%s: %s" % (self.question.question_text,
                           self.chosen_option.option_text)

    class Meta:
        ordering = ('answer_sheet', 'question__question_order',)
