from django.db import models
from django.db.models import Count
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from survey import constants


class QuestionnaireManager(models.Manager):
    """ Model manager for questionnaire models. Used mainly to determine if a
        questionnaire is available for a given user.
    """

    def questionnaire_for_user(self, user):
        """ Determine if a questionnaire is available for a given user
        """
        if not user.get_profile().decline_surveys:
            qs = self.get_query_set().filter(active=True)
            for itm in qs:
                # look for a questionnaire with available questions
                if itm.get_status(user) != constants.QUESTIONNAIRE_COMPLETED:
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
        ordering = ('date_created',)

    def get_next_question_for_user(self, user):
        """ Retrieve the next unanswered question in the questionnaire
        """
        try:
            # get the matching answersheet for the user.
            answersheet = self.answersheet_set.get(user=user)

            # if the sheet has no answers yet, return the first question
            if not answersheet.multichoiceanswer_set.exists():
                return self.multichoicequestion_set.all()[0]
            else:
                # find and return the first question without an answer
                for question in self.multichoicequestion_set.all():
                    if not answersheet.multichoiceanswer_set.filter(
                            question=question).exists():
                        return question
        except AnswerSheet.DoesNotExist:
            # no answer sheet yet
            return self.multichoicequestion_set.all()[0]

    def get_status(self, user):
        try:
            if user.get_profile().decline_surveys:
                return constants.QUESTIONNAIRE_REJECTED
        except ObjectDoesNotExist:
            pass
        qs = self.answersheet_set.filter(user=user)
        if not qs.exists():
            return constants.QUESTIONNAIRE_PENDING
        else:
            return qs[0].get_status()
        return constants.QUESTIONNAIRE_PENDING

    def number_of_questions(self):
        return self.multichoicequestion_set.count()


class EUQuizManager(models.Manager):
    """ Model manager for questionnaire models. Used mainly to determine if a
        questionnaire is available for a given user.
    """

    def home_page_quizzes(self, user):
        """ Return EU Nutrition quizzes that needs to show on the home page.
        """
        qs = self.get_query_set().filter(active=True, show_on_home_page=True)
        return [itm for itm in qs
                if itm.get_status(user) != constants.QUESTIONNAIRE_COMPLETED]


class EUNutritionQuiz(Questionnaire):
    """ Defines a model to be used to present EU Nutrition surveys linked to
        a Post. Adds a description field to display in a banner.
    """
    banner_description = models.TextField(blank=False)
    show_on_home_page = models.BooleanField(default=False)

    objects = EUQuizManager()

    class Meta:
        verbose_name = 'EU Nutrition Quiz'
        verbose_name_plural = 'EU Nutrition Quizzes'

    def get_status(self, user):
        """ Check the status of the EUQuiz for the user. Don't check the
            declined flag in the user profile.
        """
        qs = self.answersheet_set.filter(user=user.id)
        if not qs.exists():
            return constants.QUESTIONNAIRE_PENDING
        else:
            return qs[0].get_status()
        return constants.QUESTIONNAIRE_PENDING


class EUQuizToPost(models.Model):
    """ Use a similar method to NavigationLink in mama to achieve the link
        between a Post and a Quiz
    """
    post = models.ForeignKey(
        'post.Post',
        related_name="post_euquiz_set"
    )
    euquiz = models.ForeignKey(
        EUNutritionQuiz,
        related_name="euquiz_post_set"
    )

    def __unicode__(self):
        return self.euquiz.title


class QuestionnaireHolodeckKeys(models.Model):
    """ Set up the holodeck keys for the metrics being tracked.
    """
    questionnaire = models.ForeignKey(Questionnaire, blank=False)
    metric = models.PositiveSmallIntegerField(
        choices=constants.QUESTIONNAIRE_METRICS,
        blank=False)
    holodeck_key = models.CharField(max_length=100, blank=False)

    def __unicode__(self):
        return self.holodeck_key

    class Meta:
        ordering = ('questionnaire', 'metric',)


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


class AnswerSheetManager(models.Manager):
    """ Model manager for answer sheet model.
    """

    def get_max_answers(self):
        """ Used to get the maximum number of questions answered across all
            sheets, for correctly setting the headings row for the CSV export
            file.
        """
        result = 0
        qs = self.get_query_set().values('id')
        if qs:
            qs = qs.annotate(answers=Count('multichoiceanswer'))
            qs = qs.order_by('-answers')
            result = list(qs)[0]['answers']
        return result


class AnswerSheet(models.Model):
    """ Contains the answers provided by the user in response to the questions
        contained in the questionnaire.
    """
    questionnaire = models.ForeignKey(Questionnaire, blank=False)
    user = models.ForeignKey(User, blank=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_last_updated = models.DateTimeField(auto_now=True, blank=True)

    objects = AnswerSheetManager()

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

    def get_status(self):
        """ Determine the status of the user's participation in the
            questionnaire.
        """
        number_of_questions = self.questionnaire.number_of_questions()
        number_of_questions_answered = self.number_of_questions_answered()

        # If an answersheet exists, but no answers have been recorded, the
        # status is pending.
        if number_of_questions_answered == 0:
            return constants.QUESTIONNAIRE_PENDING

        # If an answersheet exists, with less answers than questions, the
        # status is incomplete.
        if (number_of_questions_answered > 0) and \
                (number_of_questions_answered < number_of_questions):
            return constants.QUESTIONNAIRE_INCOMPLETE

        # if the number of answers matches the number of questions, the status
        # is complete.
        if number_of_questions_answered == number_of_questions:
            return constants.QUESTIONNAIRE_COMPLETED

        # default status is pending
        return constants.QUESTIONNAIRE_PENDING

    def get_status_text(self):
        status = self.get_status()
        if status == constants.QUESTIONNAIRE_COMPLETED:
            return 'Completed'
        elif status == constants.QUESTIONNAIRE_INCOMPLETE:
            return 'Incomplete'
        elif status == constants.QUESTIONNAIRE_PENDING:
            return 'Pending'
        elif status == constants.QUESTIONNAIRE_REJECTED:
            return 'Rejected'
        return 'Unknown'

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
