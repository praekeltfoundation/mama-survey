from django.utils import unittest
from django.contrib.auth.models import User

from survey.models import Questionnaire, MultiChoiceQuestion, \
                          MultiChoiceOption, AnswerSheet, MultiChoiceAnswer


class SurveyTestCase(unittest.TestCase):

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
                    title = 'MAMA Questionnaire 1',
                    introduction_text = 'Intro text 1',
                    thank_you_text = 'Thank you once',
                    created_by = self.boss_man,
                    active = False)
        self.question1 = self.questionnaire1.multichoicequestion_set.create(
                    question_order = 0,
                    question_text = 'Question 1')
        self.option1 = self.question1.multichoiceoption_set.create(
                    option_order = 0,
                    option_text = 'Option 1',
                    is_correct_option = False)
        self.option2 = self.question1.multichoiceoption_set.create(
                    option_order = 1,
                    option_text = 'Option 2',
                    is_correct_option = True)

    def tearDown(self):
        self.questionnaire1.delete()
        self.guinea_pig.delete()
        self.boss_man.delete()

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
                questionnaire = self.questionnaire1,
                user=self.guinea_pig)
        self.assertEqual(
                Questionnaire.objects.questionnaire_for_user(self.guinea_pig),
                self.questionnaire1)

        # Create an answer for question 1. No questions left, so questionnaire
        # is completed, and nothing more available.
        sheet.multichoiceanswer_set.create(
                question = self.question1,
                chosen_option = self.option2)
        self.assertIsNone(
                Questionnaire.objects.questionnaire_for_user(self.guinea_pig))

    def test_get_next_question_for_user(self):
        # Add a question to questionnaire 1
        question2 = self.questionnaire1.multichoicequestion_set.create(
                    question_order = 1,
                    question_text = 'Question 2')
        option1 = question2.multichoiceoption_set.create(
                    option_order = 0,
                    option_text = 'Option 1',
                    is_correct_option = True)
        option2 = question2.multichoiceoption_set.create(
                    option_order = 1,
                    option_text = 'Option 2',
                    is_correct_option = False)

        # We should get question 1 as the next available question
        self.assertEqual(
                self.questionnaire1.get_next_question_for_user(self.guinea_pig),
                self.question1)

        # Create answersheet for questionnaire with no answers
        sheet = AnswerSheet.objects.create(
                questionnaire = self.questionnaire1,
                user=self.guinea_pig)

        # We should still get question 1 as the next available question
        self.assertEqual(
                self.questionnaire1.get_next_question_for_user(self.guinea_pig),
                self.question1)

        # Create an answer for question 1. We should expect to get question2 as
        # the next question
        sheet.multichoiceanswer_set.create(
                question = self.question1,
                chosen_option = self.option2)
        self.assertEqual(
                self.questionnaire1.get_next_question_for_user(self.guinea_pig),
                question2)

        # Create an answer for question 2. We should expect to get no next
        # question
        sheet.multichoiceanswer_set.create(
                question = question2,
                chosen_option = option1)
        self.assertIsNone(
                self.questionnaire1.get_next_question_for_user(self.guinea_pig))

    def test_answer_sheet(self):
        # Add a question to questionnaire 1
        question2 = self.questionnaire1.multichoicequestion_set.create(
                    question_order = 1,
                    question_text = 'Question 2')
        option1 = question2.multichoiceoption_set.create(
                    option_order = 0,
                    option_text = 'Option 1',
                    is_correct_option = True)
        option2 = question2.multichoiceoption_set.create(
                    option_order = 1,
                    option_text = 'Option 2',
                    is_correct_option = False)

        # Create answersheet for questionnaire with no answers
        sheet = AnswerSheet.objects.create(
                questionnaire = self.questionnaire1,
                user=self.guinea_pig)
        self.assertFalse(sheet.is_complete(self.guinea_pig))

        # Create an answer for question 1. Sheet should still be incomplete
        sheet.multichoiceanswer_set.create(
                question = self.question1,
                chosen_option = self.option2)
        self.assertFalse(sheet.is_complete(self.guinea_pig))

        # Create an answer for question 2. Sheet should be complete
        sheet.multichoiceanswer_set.create(
                question = question2,
                chosen_option = option1)
        self.assertTrue(sheet.is_complete(self.guinea_pig))

    def test_score(self):
        # Add a question to questionnaire 1
        question2 = self.questionnaire1.multichoicequestion_set.create(
                    question_order = 1,
                    question_text = 'Question 2')
        option1 = question2.multichoiceoption_set.create(
                    option_order = 0,
                    option_text = 'Option 1',
                    is_correct_option = True)
        option2 = question2.multichoiceoption_set.create(
                    option_order = 1,
                    option_text = 'Option 2',
                    is_correct_option = False)

        # Create answersheet for questionnaire with no answers
        sheet = AnswerSheet.objects.create(
                questionnaire = self.questionnaire1,
                user=self.guinea_pig)
        self.assertEqual(sheet.calculate_score(self.guinea_pig), 0)

        # Create a correct answer for question1
        sheet.multichoiceanswer_set.create(
                question = self.question1,
                chosen_option = self.option2)
        self.assertEqual(sheet.calculate_score(self.guinea_pig), 1)

        # Create an incorrect answer for question 2.
        sheet.multichoiceanswer_set.create(
                question = question2,
                chosen_option = option2)
        self.assertEqual(sheet.calculate_score(self.guinea_pig), 1)
