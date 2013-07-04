# -*- coding: utf-8 -*-

from StringIO import StringIO

from django.utils import unittest
from django.db.utils import IntegrityError
from django.contrib.auth.models import User

from survey import constants
from survey.management.commands import survey_answersheet_csv_export
from survey.models import (Questionnaire, MultiChoiceQuestion,
                           MultiChoiceOption, AnswerSheet, MultiChoiceAnswer)


class BaseSurveyTestCase(unittest.TestCase):

    def setUp(self):
        self.boss_man = User.objects.create(username='boss',
                                            password='bigsecret')
        self.boss_man.is_active = True
        self.boss_man.is_staff = True
        self.boss_man.is_superuser = True
        self.boss_man.save()

        self.guinea_pig = User.objects.create(username='thepig',
                                              password='dirtysecret')
        self.guinea_pig.active = True
        self.guinea_pig.save()

        self.questionnaire1 = Questionnaire.objects.create(
            title='MAMA Questionnaire 1',
            introduction_text='Intro text 1',
            thank_you_text='Thank you once',
            created_by=self.boss_man,
            active=False)
        self.question1 = self.questionnaire1.multichoicequestion_set.create(
            question_order=0,
            question_text='Question 1')
        self.option1 = self.question1.multichoiceoption_set.create(
            option_order=0,
            option_text='Option 1',
            is_correct_option=False)
        self.option2 = self.question1.multichoiceoption_set.create(
            option_order=1,
            option_text='Option 2',
            is_correct_option=True)

    def tearDown(self):
        self.questionnaire1.delete()
        self.guinea_pig.delete()
        self.boss_man.delete()


class SurveyTestCase(BaseSurveyTestCase):

    def test_number_of_questions(self):
        self.assertEqual(self.questionnaire1.number_of_questions(), 1)

        # Add a question to questionnaire 1
        question2 = self.questionnaire1.multichoicequestion_set.create(
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

        self.assertEqual(self.questionnaire1.number_of_questions(), 2)

    def test_available_questionnaire_for_user(self):
        # An inactive qeustionnaire is not available
        self.assertIsNone(
            Questionnaire.objects.questionnaire_for_user(self.guinea_pig))

        # Set state to active
        self.questionnaire1.active = True
        self.questionnaire1.save()
        self.assertEqual(
            Questionnaire.objects.questionnaire_for_user(self.guinea_pig),
            self.questionnaire1)

        # Create answersheet for questionnaire with no answers
        sheet = AnswerSheet.objects.create(
            questionnaire=self.questionnaire1,
            user=self.guinea_pig)
        self.assertEqual(
            Questionnaire.objects.questionnaire_for_user(self.guinea_pig),
            self.questionnaire1)

        # Create an answer for question 1. No questions left, so questionnaire
        # is completed, and nothing more available.
        sheet.multichoiceanswer_set.create(
            question=self.question1,
            chosen_option=self.option2)
        self.assertIsNone(
            Questionnaire.objects.questionnaire_for_user(self.guinea_pig))

        # create a new questionnaire
        questionnaire2 = Questionnaire.objects.create(
            title='MAMA Questionnaire 2',
            introduction_text='Intro text 2',
            thank_you_text='Thank you twice',
            created_by=self.boss_man,
            active=True)
        self.assertEqual(
            Questionnaire.objects.questionnaire_for_user(self.guinea_pig),
            questionnaire2)

        # create a new user
        guinea_pig3 = User.objects.create(username='thepig3',
                                          password='dirtysecret3')
        guinea_pig3.active = True
        self.assertEqual(
            Questionnaire.objects.questionnaire_for_user(guinea_pig3),
            self.questionnaire1)

    def test_get_next_question_for_user(self):
        # Add a question to questionnaire 1
        question2 = self.questionnaire1.multichoicequestion_set.create(
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

        # We should get question 1 as the next available question
        self.assertEqual(
            self.questionnaire1.get_next_question_for_user(self.guinea_pig),
            self.question1)

        # Create answersheet for questionnaire with no answers
        sheet = AnswerSheet.objects.create(
            questionnaire=self.questionnaire1,
            user=self.guinea_pig)

        # We should still get question 1 as the next available question
        self.assertEqual(
            self.questionnaire1.get_next_question_for_user(self.guinea_pig),
            self.question1)

        # Create an answer for question 1. We should expect to get question2 as
        # the next question
        sheet.multichoiceanswer_set.create(
            question=self.question1,
            chosen_option=self.option2)
        self.assertEqual(
            self.questionnaire1.get_next_question_for_user(self.guinea_pig),
            question2)

        # Create an answer for question 2. We should expect to get no next
        # question
        sheet.multichoiceanswer_set.create(
            question=question2,
            chosen_option=option1)
        self.assertIsNone(
            self.questionnaire1.get_next_question_for_user(self.guinea_pig))

    def test_answer_sheet(self):
        # Add a question to questionnaire 1
        question2 = self.questionnaire1.multichoicequestion_set.create(
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

        # Create answersheet for questionnaire with no answers
        sheet = AnswerSheet.objects.create(
            questionnaire=self.questionnaire1,
            user=self.guinea_pig)
        self.assertEqual(sheet.get_status(), constants.QUESTIONNAIRE_PENDING)
        self.assertEqual(sheet.get_status_text(), 'Pending')
        self.assertEqual(self.questionnaire1.get_status(self.guinea_pig),
                         constants.QUESTIONNAIRE_PENDING)

        # Create an answer for question 1. Sheet should still be incomplete
        sheet.multichoiceanswer_set.create(
            question=self.question1,
            chosen_option=self.option2)
        self.assertEqual(sheet.get_status(),
                         constants.QUESTIONNAIRE_INCOMPLETE)
        self.assertEqual(sheet.get_status_text(), 'Incomplete')
        self.assertEqual(self.questionnaire1.get_status(self.guinea_pig),
                         constants.QUESTIONNAIRE_INCOMPLETE)

        # Check the number of questions answered
        self.assertEqual(sheet.number_of_questions_answered(), 1)

        # Create an answer for question 2. Sheet should be complete
        sheet.multichoiceanswer_set.create(
            question=question2,
            chosen_option=option1)
        self.assertEqual(sheet.get_status(), constants.QUESTIONNAIRE_COMPLETED)
        self.assertEqual(sheet.get_status_text(), 'Completed')
        self.assertEqual(self.questionnaire1.get_status(self.guinea_pig),
                         constants.QUESTIONNAIRE_COMPLETED)

        # The questionnaire must incomplete for another user
        guinea_pig4 = User.objects.create(username='thepig4',
                                          password='dirtysecret4')
        guinea_pig4.active = True
        self.assertEqual(self.questionnaire1.get_status(guinea_pig4),
                         constants.QUESTIONNAIRE_PENDING)

        # Check the number of questions answered
        self.assertEqual(sheet.number_of_questions_answered(), 2)

    def test_score(self):
        # Add a question to questionnaire 1
        question2 = self.questionnaire1.multichoicequestion_set.create(
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

        # Create answersheet for questionnaire with no answers
        sheet = AnswerSheet.objects.create(
            questionnaire=self.questionnaire1,
            user=self.guinea_pig)
        self.assertEqual(sheet.calculate_score(), 0)

        # Create a correct answer for question1
        sheet.multichoiceanswer_set.create(
            question=self.question1,
            chosen_option=self.option2)
        self.assertEqual(sheet.calculate_score(), 1)

        # Create an incorrect answer for question 2.
        sheet.multichoiceanswer_set.create(
            question=question2,
            chosen_option=option2)
        self.assertEqual(sheet.calculate_score(), 1)

        # Create another sheet for a different user
        guinea_pig2 = User.objects.create(username='thepig2',
                                          password='dirtysecret2')
        guinea_pig2.active = True
        sheet2 = AnswerSheet.objects.create(
            questionnaire=self.questionnaire1,
            user=guinea_pig2)

        # Create a correct answer for question1
        sheet2.multichoiceanswer_set.create(
            question=self.question1,
            chosen_option=self.option2)
        self.assertEqual(sheet2.calculate_score(), 1)

        # Create an correct answer for question 2.
        sheet2.multichoiceanswer_set.create(
            question=question2,
            chosen_option=option1)
        self.assertEqual(sheet2.calculate_score(), 2)

    def test_unique(self):
        # check for integrity error violations
        guinea_pig3, created = User.objects.get_or_create(
            username='thepig3',
            password='dirtysecret3')
        guinea_pig3.active = True

        sheet1 = AnswerSheet.objects.create(
            questionnaire=self.questionnaire1,
            user=self.guinea_pig)
        self.assertRaises(IntegrityError,
                          AnswerSheet.objects.create,
                          questionnaire=self.questionnaire1,
                          user=self.guinea_pig)
        sheet2 = AnswerSheet.objects.create(
            questionnaire=self.questionnaire1,
            user=guinea_pig3)
        self.assertIsNotNone(sheet2)
        self.assertNotEqual(sheet1, sheet2)

    def test_max_answers(self):
        # Test the maximum answers method on the answersheet manager.

        # No answers yet
        self.assertEqual(AnswerSheet.objects.get_max_answers(), 0)

        sheet = AnswerSheet.objects.create(
            questionnaire=self.questionnaire1,
            user=self.guinea_pig)

        # Create an answer for question1
        sheet.multichoiceanswer_set.create(
            question=self.question1,
            chosen_option=self.option2)
        self.assertEqual(AnswerSheet.objects.get_max_answers(), 1)

        guinea_pig3, created = User.objects.get_or_create(
            username='thepig3',
            password='dirtysecret3')
        guinea_pig3.active = True

        # Create another sheet ans add an answer
        sheet1 = AnswerSheet.objects.create(
            questionnaire=self.questionnaire1,
            user=guinea_pig3)
        sheet1.multichoiceanswer_set.create(
            question=self.question1,
            chosen_option=self.option2)
        self.assertEqual(AnswerSheet.objects.get_max_answers(), 1)

        # Add another question
        question2 = self.questionnaire1.multichoicequestion_set.create(
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


class SurveyCommandsTestCase(BaseSurveyTestCase):

    def test_unicode_output(self):
        # Add a user with a unicode username
        foreigner = User.objects.create(username=u'Ťũńŏřęķ',
                                        password='noneofyourbusiness')

        # Add a question to questionnaire 1
        question2 = self.questionnaire1.multichoicequestion_set.create(
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
            questionnaire=self.questionnaire1,
            user=foreigner)
        sheet.multichoiceanswer_set.create(
            question=self.question1,
            chosen_option=self.option2)
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
