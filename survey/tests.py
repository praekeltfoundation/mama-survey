# -*- coding: utf-8 -*-

from mock import patch

from StringIO import StringIO

from django.utils import unittest
from django.db.utils import IntegrityError, DatabaseError
from django.contrib.auth.models import User

from survey import constants
from survey.management.commands import survey_answersheet_csv_export
from survey.models import (Questionnaire, ContentQuiz, MultiChoiceQuestion,
                           MultiChoiceOption, AnswerSheet, MultiChoiceAnswer)
from post.models import Post


class DummyProfile(object):

    def __init__(self, decline):
        self.decline_surveys = decline


class BaseSurveyTestCase(unittest.TestCase):

    def create_boss_man(self):
        boss_man = User.objects.create(username='boss',
                                       password='bigsecret')
        boss_man.is_active = True
        boss_man.is_staff = True
        boss_man.is_superuser = True
        boss_man.save()
        return boss_man

    def create_guinea_pig(self, username):
        guinea_pig = User.objects.create(username=username,
                                         password='dirtysecret')
        guinea_pig.active = True
        guinea_pig.save()
        return guinea_pig

    def create_questionnaire(self, owner):
        questionnaire = Questionnaire.objects.create(
            title='MAMA Questionnaire',
            introduction_text='Intro text',
            thank_you_text='Thank you text',
            created_by=owner,
            active=False)
        question1 = questionnaire.multichoicequestion_set.create(
            question_order=0,
            question_text='Question 1')
        option1 = question1.multichoiceoption_set.create(
            option_order=0,
            option_text='Option 1',
            is_correct_option=False)
        option2 = question1.multichoiceoption_set.create(
            option_order=1,
            option_text='Option 2',
            is_correct_option=True)
        return questionnaire

    def get_question1(self, questionnaire):
        return questionnaire.multichoicequestion_set.filter(
            question_text='Question 1').get()

    def get_option2(self, question1):
        return question1.multichoiceoption_set.filter(
            option_text='Option 2').get()


class SurveyTestCase(BaseSurveyTestCase):

    def test_number_of_questions(self):
        boss_man = self.create_boss_man()
        questionnaire1 = self.create_questionnaire(boss_man)

        self.assertEqual(questionnaire1.number_of_questions(), 1)

        # Add a question to questionnaire 1
        question2 = questionnaire1.multichoicequestion_set.create(
            question_order=1,
            question_text='Question 2')
        option1 = question2.multichoiceoption_set.create(
            option_order=0,
            option_text='Option 1',
            is_correct_option=True)
        option2 = question2.multichoiceoption_set.create(
            option_order=1,
            option_text='Option 2',
            is_correct_option=False)

        self.assertEqual(questionnaire1.number_of_questions(), 2)

        questionnaire1.delete()
        boss_man.delete()

    @patch.object(User, 'get_profile')
    def test_available_questionnaire_for_user(self, get_profile):
        # An inactive qeustionnaire is not available
        get_profile.return_value = DummyProfile(False)

        boss_man = self.create_boss_man()
        questionnaire1 = self.create_questionnaire(boss_man)
        guinea_pig = self.create_guinea_pig('thepig')

        self.assertIsNone(
            Questionnaire.objects.questionnaire_for_user(guinea_pig))

        # Set state to active
        questionnaire1.active = True
        questionnaire1.save()
        self.assertEqual(
            Questionnaire.objects.questionnaire_for_user(guinea_pig),
            questionnaire1)

        # Create answersheet for questionnaire with no answers
        sheet = AnswerSheet.objects.create(
            questionnaire=questionnaire1,
            user=guinea_pig)
        self.assertEqual(
            Questionnaire.objects.questionnaire_for_user(guinea_pig),
            questionnaire1)

        # Create an answer for question 1. No questions left, so questionnaire
        # is completed, and nothing more available.
        question1 = self.get_question1(questionnaire1)
        option2 = self.get_option2(question1)
        sheet.multichoiceanswer_set.create(
            question=question1,
            chosen_option=option2)
        self.assertIsNone(
            Questionnaire.objects.questionnaire_for_user(guinea_pig))

        # create a new questionnaire
        questionnaire2 = Questionnaire.objects.create(
            title='MAMA Questionnaire 2',
            introduction_text='Intro text 2',
            thank_you_text='Thank you twice',
            created_by=boss_man,
            active=True)
        self.assertEqual(
            Questionnaire.objects.questionnaire_for_user(guinea_pig),
            questionnaire2)

        # create another questionnaire
        questionnaire3 = Questionnaire.objects.create(
            title='MAMA Questionnaire 3',
            introduction_text='Intro text 3',
            thank_you_text='Thank you thrice',
            created_by=boss_man,
            active=True)

        #ensure questionnaire 2 cannot be answered if questionnaire 3 is unanswered
        questionnaire2.target_survey_users = questionnaire3
        questionnaire2.save()
        self.assertEqual(
            Questionnaire.objects.questionnaire_for_user(guinea_pig),
            questionnaire3)

        questionnaire1.delete()
        boss_man.delete()
        guinea_pig.delete()

    @patch.object(User, 'get_profile')
    def test_available_questionnaire_for_declined_user(self, get_profile):
        get_profile.return_value = DummyProfile(True)

        boss_man = self.create_boss_man()
        questionnaire1 = self.create_questionnaire(boss_man)
        # create a new user
        guinea_pig = self.create_guinea_pig('thepig6')

        self.assertIsNone(
            Questionnaire.objects.questionnaire_for_user(guinea_pig))

        questionnaire1.delete()
        boss_man.delete()
        guinea_pig.delete()

    def test_get_next_question_for_user(self):
        boss_man = self.create_boss_man()
        questionnaire1 = self.create_questionnaire(boss_man)

        # Add a question to questionnaire 1
        question2 = questionnaire1.multichoicequestion_set.create(
            question_order=1,
            question_text='Question 2')
        option1 = question2.multichoiceoption_set.create(
            option_order=0,
            option_text='Option 1',
            is_correct_option=True)
        option2 = question2.multichoiceoption_set.create(
            option_order=1,
            option_text='Option 2',
            is_correct_option=False)

        guinea_pig = self.create_guinea_pig('thepig')

        # We should get question 1 as the next available question
        question1 = self.get_question1(questionnaire1)
        self.assertEqual(
            questionnaire1.get_next_question_for_user(guinea_pig),
            question1)

        # Create answersheet for questionnaire with no answers
        sheet = AnswerSheet.objects.create(
            questionnaire=questionnaire1,
            user=guinea_pig)

        # We should still get question 1 as the next available question
        self.assertEqual(
            questionnaire1.get_next_question_for_user(guinea_pig),
            question1)

        # Create an answer for question 1. We should expect to get question2 as
        # the next question
        sheet.multichoiceanswer_set.create(
            question=question1,
            chosen_option=option2)
        self.assertEqual(
            questionnaire1.get_next_question_for_user(guinea_pig),
            question2)

        # Create an answer for question 2. We should expect to get no next
        # question
        sheet.multichoiceanswer_set.create(
            question=question2,
            chosen_option=option1)
        self.assertIsNone(
            questionnaire1.get_next_question_for_user(guinea_pig))

        questionnaire1.delete()
        boss_man.delete()
        guinea_pig.delete()

    @patch.object(User, 'get_profile')
    def test_answer_sheet(self, get_profile):
        get_profile.return_value = DummyProfile(False)

        boss_man = self.create_boss_man()
        questionnaire1 = self.create_questionnaire(boss_man)

        # Add a question to questionnaire 1
        question2 = questionnaire1.multichoicequestion_set.create(
            question_order=1,
            question_text='Question 2')
        option1 = question2.multichoiceoption_set.create(
            option_order=0,
            option_text='Option 1',
            is_correct_option=True)
        option2 = question2.multichoiceoption_set.create(
            option_order=1,
            option_text='Option 2',
            is_correct_option=False)

        guinea_pig = self.create_guinea_pig('thepig')

        # Create answersheet for questionnaire with no answers
        sheet = AnswerSheet.objects.create(
            questionnaire=questionnaire1,
            user=guinea_pig)
        self.assertEqual(sheet.get_status(), constants.QUESTIONNAIRE_PENDING)
        self.assertEqual(sheet.get_status_text(), 'Pending')
        self.assertEqual(questionnaire1.get_status(guinea_pig),
                         constants.QUESTIONNAIRE_PENDING)

        # Create an answer for question 1. Sheet should still be incomplete
        question1 = self.get_question1(questionnaire1)
        sheet.multichoiceanswer_set.create(
            question=question1,
            chosen_option=option2)
        self.assertEqual(sheet.get_status(),
                         constants.QUESTIONNAIRE_INCOMPLETE)
        self.assertEqual(sheet.get_status_text(), 'Incomplete')
        self.assertEqual(questionnaire1.get_status(guinea_pig),
                         constants.QUESTIONNAIRE_INCOMPLETE)

        # Check the number of questions answered
        self.assertEqual(sheet.number_of_questions_answered(), 1)

        # Create an answer for question 2. Sheet should be complete
        sheet.multichoiceanswer_set.create(
            question=question2,
            chosen_option=option1)
        self.assertEqual(sheet.get_status(), constants.QUESTIONNAIRE_COMPLETED)
        self.assertEqual(sheet.get_status_text(), 'Completed')
        self.assertEqual(questionnaire1.get_status(guinea_pig),
                         constants.QUESTIONNAIRE_COMPLETED)

        # The questionnaire must incomplete for another user
        guinea_pig4 = self.create_guinea_pig('thepig4')
        self.assertEqual(questionnaire1.get_status(guinea_pig4),
                         constants.QUESTIONNAIRE_PENDING)

        # Check the number of questions answered
        self.assertEqual(sheet.number_of_questions_answered(), 2)

        questionnaire1.delete()
        boss_man.delete()
        guinea_pig.delete()
        guinea_pig4.delete()

    def test_score(self):
        boss_man = self.create_boss_man()
        questionnaire1 = self.create_questionnaire(boss_man)

        # Add a question to questionnaire 1
        question2 = questionnaire1.multichoicequestion_set.create(
            question_order=1,
            question_text='Question 2')
        q2option1 = question2.multichoiceoption_set.create(
            option_order=0,
            option_text='Option 1',
            is_correct_option=True)
        q2option2 = question2.multichoiceoption_set.create(
            option_order=1,
            option_text='Option 2',
            is_correct_option=False)

        guinea_pig = self.create_guinea_pig('thepig')

        # Create answersheet for questionnaire with no answers
        sheet = AnswerSheet.objects.create(
            questionnaire=questionnaire1,
            user=guinea_pig)
        self.assertEqual(sheet.calculate_score(), 0)

        # Create a correct answer for question1
        question1 = self.get_question1(questionnaire1)
        option2 = self.get_option2(question1)
        sheet.multichoiceanswer_set.create(
            question=question1,
            chosen_option=option2)
        self.assertEqual(sheet.calculate_score(), 1)

        # Create an incorrect answer for question 2.
        sheet.multichoiceanswer_set.create(
            question=question2,
            chosen_option=q2option2)
        self.assertEqual(sheet.calculate_score(), 1)

        # Create another sheet for a different user
        guinea_pig2 = self.create_guinea_pig('thepig2')
        sheet2 = AnswerSheet.objects.create(
            questionnaire=questionnaire1,
            user=guinea_pig2)

        # Create a correct answer for question1
        sheet2.multichoiceanswer_set.create(
            question=question1,
            chosen_option=option2)
        self.assertEqual(sheet2.calculate_score(), 1)

        # Create an correct answer for question 2.
        sheet2.multichoiceanswer_set.create(
            question=question2,
            chosen_option=q2option1)
        self.assertEqual(sheet2.calculate_score(), 2)

        questionnaire1.delete()
        boss_man.delete()
        guinea_pig.delete()
        guinea_pig2.delete()

    def test_unique(self):
        boss_man = self.create_boss_man()
        questionnaire1 = self.create_questionnaire(boss_man)
        guinea_pig = self.create_guinea_pig('thepig')

        # check for integrity error violations
        sheet1 = AnswerSheet.objects.create(
            questionnaire=questionnaire1,
            user=guinea_pig)
        self.assertRaises(IntegrityError,
                          AnswerSheet.objects.create,
                          questionnaire=questionnaire1,
                          user=guinea_pig)

        questionnaire1.delete()
        boss_man.delete()
        guinea_pig.delete()

    def test_not_thesame(self):
        boss_man = self.create_boss_man()
        questionnaire1 = self.create_questionnaire(boss_man)

        # test that 2 objects are not the same
        guinea_pig = self.create_guinea_pig('thepig')

        gp = User.objects.create(
            username='thepig5',
            password='dirtysecret5')
        gp.active = True

        sheet1 = AnswerSheet.objects.create(
            questionnaire=questionnaire1,
            user=guinea_pig)
        sheet2 = AnswerSheet.objects.create(
            questionnaire=questionnaire1,
            user=gp)
        self.assertIsNotNone(sheet2)
        self.assertNotEqual(sheet1, sheet2)

        questionnaire1.delete()
        boss_man.delete()
        guinea_pig.delete()
        gp.delete()

    def test_max_answers(self):
        boss_man = self.create_boss_man()
        questionnaire1 = self.create_questionnaire(boss_man)

        # Test the maximum answers method on the answersheet manager.
        guinea_pig = self.create_guinea_pig('thepig')

        # No answers yet
        self.assertEqual(AnswerSheet.objects.get_max_answers(), 0)

        sheet = AnswerSheet.objects.create(
            questionnaire=questionnaire1,
            user=guinea_pig)

        # Create an answer for question1
        question1 = self.get_question1(questionnaire1)
        option2 = self.get_option2(question1)
        sheet.multichoiceanswer_set.create(
            question=question1,
            chosen_option=option2)
        self.assertEqual(AnswerSheet.objects.get_max_answers(), 1)

        guinea_pig3 = self.create_guinea_pig('thepig3')

        # Create another sheet ans add an answer
        sheet1 = AnswerSheet.objects.create(
            questionnaire=questionnaire1,
            user=guinea_pig3)
        sheet1.multichoiceanswer_set.create(
            question=question1,
            chosen_option=option2)
        self.assertEqual(AnswerSheet.objects.get_max_answers(), 1)

        # Add another question
        question2 = questionnaire1.multichoicequestion_set.create(
            question_order=1,
            question_text='Question 2 again')
        option1 = question2.multichoiceoption_set.create(
            option_order=0,
            option_text='Option 1 again',
            is_correct_option=True)
        option2 = question2.multichoiceoption_set.create(
            option_order=1,
            option_text='Option 2 again',
            is_correct_option=False)

        # Add another answer
        sheet1.multichoiceanswer_set.create(
            question=question2,
            chosen_option=option2)
        self.assertEqual(AnswerSheet.objects.get_max_answers(), 2)

        questionnaire1.delete()
        boss_man.delete()
        guinea_pig.delete()
        guinea_pig3.delete()


class SurveyCommandsTestCase(BaseSurveyTestCase):

    def test_unicode_output(self):
        boss_man = self.create_boss_man()
        questionnaire1 = self.create_questionnaire(boss_man)

        # Add a user with a unicode username
        foreigner = User.objects.create(username=u'Ťũńŏřęķ',
                                        password='noneofyourbusiness')

        # Add a question to questionnaire 1
        question2 = questionnaire1.multichoicequestion_set.create(
            question_order=1,
            question_text='Question 2')
        option1 = question2.multichoiceoption_set.create(
            option_order=0,
            option_text='Option 1',
            is_correct_option=True)
        option2 = question2.multichoiceoption_set.create(
            option_order=1,
            option_text='Option 2',
            is_correct_option=False)

        # Create an answersheet for the foreigner
        sheet = AnswerSheet.objects.create(
            questionnaire=questionnaire1,
            user=foreigner)
        question1 = self.get_question1(questionnaire1)
        sheet.multichoiceanswer_set.create(
            question=question1,
            chosen_option=option2)
        sheet.multichoiceanswer_set.create(
            question=question2,
            chosen_option=option1)

        # generate the output file
        mock_file = StringIO()
        command = survey_answersheet_csv_export.Command()
        command.get_file = lambda fn: mock_file
        command.close_file = lambda fp: True
        command.generate_file_name = lambda: 'foo.csv'
        command.handle()
        csv_data = mock_file.getvalue()

        # check for a unicode string in the output
        self.assertIn(u'Ťũńŏřęķ', csv_data.decode('utf-8'))

        questionnaire1.delete()
        boss_man.delete()


class ContentQuizTestCase(BaseSurveyTestCase):
    """ Test the functionality of the Content Linked Survey
    """
    @patch.object(User, 'get_profile')
    def test_content_quiz(self, get_profile):
        get_profile.return_value = DummyProfile(False)

        boss_man = self.create_boss_man()
        questionnaire1 = self.create_questionnaire(boss_man)
        guinea_pig = self.create_guinea_pig('thepig')

        # Create a post for the Content Quiz to hang off of
        post = Post.objects.create(
            content='This is Test content',
            state='published',
            slug='test-content',
            title='Test Content',
            owner=boss_man
        )

        # Create an inactive Content quiz
        content_quiz = ContentQuiz.objects.create(
            banner_description='This is an Content banner',
            introduction_text='Content Intro text',
            thank_you_text='Content Thank you',
            created_by=boss_man,
            active=False
        )
        content_question1 = content_quiz.multichoicequestion_set.create(
            question_order=0,
            question_text='Content Question 1')
        content_option1 = content_question1.multichoiceoption_set.create(
            option_order=0,
            option_text='Content Option 1',
            is_correct_option=False)
        content_option2 = content_question1.multichoiceoption_set.create(
            option_order=1,
            option_text='Content Option 2',
            is_correct_option=True)

        # Check that we get the active questionnaire instance, and not the
        # Content
        # Quiz instance.
        questionnaire1.active = True
        questionnaire1.save()
        self.assertEqual(
            Questionnaire.objects.questionnaire_for_user(guinea_pig),
            questionnaire1)

        # Set the active flag to True for the Content Quiz, and check that we
        # still get the normal questionnaire as the next one.
        content_quiz.active = True
        content_quiz.save()
        self.assertEqual(
            Questionnaire.objects.questionnaire_for_user(guinea_pig),
            questionnaire1)

        # Check that we don't get quizzes on the home page that don't have the
        # flag set.
        self.assertEqual(
            ContentQuiz.objects.home_page_quizzes(guinea_pig),
            [])

        # Check that we get only Content quizzes on the home page, when getting
        # what is available for the user.
        content_quiz.show_on_home_page = True
        content_quiz.save()
        self.assertIn(
            content_quiz,
            ContentQuiz.objects.home_page_quizzes(guinea_pig))

        boss_man.delete()
        questionnaire1.delete()
        guinea_pig.delete()
