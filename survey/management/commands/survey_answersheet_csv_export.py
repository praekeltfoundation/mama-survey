""" Cron-able script to store a CSV export file of answersheets on disk to be
    emailed to interested recipients.
"""
import datetime

from snippetscream.csv_serializer import UnicodeWriter
from django.core.management.base import BaseCommand
from django.db.models import Count

from survey import constants
from survey.models import AnswerSheet


class Command(BaseCommand):
    help = "Saves askMAMA answersheet results as CSV file"

    def handle(self, *args, **options):
        # generate a name for the CSV file
        now = datetime.datetime.now()
        filedate = "%04d%02d%02d" % (now.year, now.month, now.day)
        filename = "askMAMA_Survey_Answers_%s.csv" % (filedate)

        # determine the maximum answers to display per sheet
        max_answers = AnswerSheet.objects.get_max_answers()

        outfile = open(filename, 'wt')

        # create the csv writer
        writer = UnicodeWriter(outfile)

        # construct the header line
        header_line = ['User', 'Questionnaire', 'Date Submitted',
                       'Status', 'Score']
        for idx in range(max_answers):
            header_line.append('Question %s' % (idx+1))
            header_line.append('Answer %s' % (idx+1))

        # write the header line
        writer.writerow(header_line)

        # loop through the database data to build the response
        qs = AnswerSheet.objects.all().order_by('questionnaire', 'user')
        for sheet in qs:
            data = [sheet.user.username, sheet.questionnaire.title,
                    "%s" % sheet.date_created,
                    sheet.get_status_text(),
                    "%s" % sheet.calculate_score()
                    ]
            for answer in sheet.multichoiceanswer_set.all():
                data.append(answer.question.question_text)
                data.append(answer.chosen_option.option_text)
            writer.writerow(data)

        outfile.close()
