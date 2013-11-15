""" Cron-able script to store a CSV export file of answersheets on disk to be
    emailed to interested recipients.
"""
import datetime
import logging

from snippetscream.csv_serializer import UnicodeWriter
from django.core.management.base import BaseCommand

from survey.models import AnswerSheet

logger = logging.getLogger('survey_answersheet_csv_export')


class Command(BaseCommand):
    help = "Saves askMAMA answersheet results as CSV file"

    def generate_file_name(self):
        now = datetime.datetime.now()
        filedate = "%04d%02d%02d" % (now.year, now.month, now.day)
        filename = "askMAMA_Survey_Answers_%s.csv" % (filedate)
        return filename

    def get_file(self, filename):
        return open(filename, 'wt')

    def close_file(self, fp):
        return fp.close()

    def handle(self, *args, **options):
        # generate a name for the CSV file

        # determine the maximum answers to display per sheet
        max_answers = AnswerSheet.objects.get_max_answers()

        # open the output file
        filename = self.generate_file_name()
        outfile = self.get_file(filename)

        # create the csv writer
        writer = UnicodeWriter(outfile)

        # construct the header line
        header_line = ['User', 'msisdn', 'Questionnaire', 'Date Submitted',
                       'Status', 'Score']
        for idx in range(max_answers):
            header_line.append('Question %s' % (idx+1))
            header_line.append('Answer %s' % (idx+1))

        # write the header line
        writer.writerow(header_line)

        # loop through the database data to build the response
        qs = AnswerSheet.objects.all().order_by(
            'questionnaire', 'user')
        for sheet in qs:
            user = sheet.user
            msisdn = user.profile.mobile_number
            if msisdn is None:
                msisdn = u'Unknown'
            data = [user.username, msisdn,
                    sheet.questionnaire.title,
                    "%s" % sheet.date_created,
                    sheet.get_status_text(),
                    "%s" % sheet.calculate_score()
                    ]
            for answer in sheet.multichoiceanswer_set.all():
                data.append(answer.question.question_text)
                data.append(answer.chosen_option.option_text)
            writer.writerow(data)

        self.close_file(outfile)
