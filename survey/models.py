from django.db import models
from django.contrib.auth.models import User


class QuestionnaireManager(models.Manager):
    """ Model manager for questionnaire models. Used mainly to determine if a 
        questionnaire is available for a given user.
    """

    def questionnaire_for_user(self, user):
        """ Determine if a questionnaire is available for a given user
        """
        qs = self.get_query_set().filter(active=True)
        for itm in qs:
            # look for a questionnaire with available questions
            if not itm.is_complete(user):
                return itm


class Questionnaire(models.Model):
    """ Defines an available Questionnaire
    """
    title = models.CharField(max_length=100, blank=False)
    introduction_text = models.TextField(blank=False)
    thank_you_text = models.TextField(blank=False)
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, blank=False)
    active = models.BooleanField(default=False)

    objects = QuestionnaireManager()

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ('-date_created',)

    def get_next_question_for_user(self, user):
        """ Retrieve the next unanswered question in the questionnaire
        """
        try:
            # get the matching answersheet for the user.
            answersheet = self.answersheet_set.get(user=user)

            # if the sheet has no answers yet, return the first question
            if answersheet.multichoiceanswer_set.count() == 0:
                return self.multichoicequestion_set.all()[0]
            else:
                # find and return the first question without an answer
                for question in self.multichoicequestion_set.all():
                    if answersheet.multichoiceanswer_set.filter(
                                question=question).count() == 0:
                        return question
        except AnswerSheet.DoesNotExist:
            # no answer sheet yet
            return self.multichoicequestion_set.all()[0]
    
    def is_complete(self, user):
        try:
            return self.answersheet_set.filter(user=user)[0].is_complete()
        except IndexError:
            pass

    def number_of_questions(self):
        return self.multichoicequestion_set.count()


class MultiChoiceQuestion(models.Model):
    """ Defines a multiple choice type question on the questionnaire
    """
    questionnaire = models.ForeignKey(Questionnaire, blank=False)
    question_order = models.PositiveIntegerField(blank=False)
    question_text = models.CharField(max_length=255, blank=False)

    def __unicode__(self):
        return self.question_text

    class Meta:
        ordering = ('questionnaire', 'question_order',)

    
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
    questionnaire = models.ForeignKey(Questionnaire, blank=False)
    user = models.ForeignKey(User, blank=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_last_updated = models.DateTimeField(auto_now=True, blank=True)

    def __unicode__(self):
        return "%s by %s" % (self.questionnaire.title, self.user.username)

    class Meta:
        ordering = ('user', 'date_created',)
        unique_together = ('questionnaire', 'user',)

    def number_of_questions_answered(self):
        """ return the number of answered questions for a user for this sheet
        """
        # return self.multichoiceanswer_set.filter(answer_sheet=self).count()
        return self.multichoiceanswer_set.count()

    def is_complete(self):
        """ Determine if a user has completed the questionnaire
        """
        return (self.questionnaire.number_of_questions() == 
                self.number_of_questions_answered())

    def calculate_score(self):
        """ calculate the user's score.
        """
        score = 0
        for itm in self.multichoiceanswer_set.all():
            if itm.chosen_option.is_correct_option:
                score += 1
        return score


class MultiChoiceAnswer(models.Model):
    """ Store the answer option that the user selected
    """
    answer_sheet = models.ForeignKey(AnswerSheet, blank=False)
    question = models.ForeignKey(MultiChoiceQuestion, blank=False)
    chosen_option = models.ForeignKey(MultiChoiceOption, blank=False)

    def __unicode__(self):
        return "%s: %s" % (self.question.question_text,
                           self.chosen_option.option_text)

    class Meta:
        ordering = ('answer_sheet', 'question__question_order',)
