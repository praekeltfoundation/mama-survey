import csv
import datetime
from snippetscream.csv_serializer import UnicodeWriter

from django.contrib import admin
from django.conf.urls.defaults import patterns, url
from django.db.models import Count
from django.http import HttpResponse

from survey import constants
from survey.models import (Questionnaire, MultiChoiceQuestion,
                           MultiChoiceOption, QuestionnaireHolodeckKeys,
                           AnswerSheet, MultiChoiceAnswer)


class MultiChoiceOptionAdmin(admin.TabularInline):
    model = MultiChoiceOption


class MultiChoiceQuestionAdmin(admin.ModelAdmin):
    list_display = ('questionnaire', 'question_order', 'question_text',)
    raw_id_fields = ('questionnaire',)
    inlines = (MultiChoiceOptionAdmin,)

admin.site.register(MultiChoiceQuestion, MultiChoiceQuestionAdmin)


class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'date_created', 'active',)
    date_hierarchy = 'date_created'
    search_fields = ('title', 'created_by',)
    list_filter = ('active',)
    read_only_fields = ('date_created',)
    raw_id_fields = ('created_by',)

admin.site.register(Questionnaire, QuestionnaireAdmin)


class MultiChoiceAnswerAdmin(admin.TabularInline):
    model = MultiChoiceAnswer
    raw_id_fields = ('answer_sheet',)


class AnswerSheetAdmin(admin.ModelAdmin):
    list_display = ('questionnaire', 'user', 'date_created',)
    date_hierarchy = 'date_created'
    search_fields = ('questionnaire', 'user',)
    read_only_fields = ('date_created',)
    raw_id_fields = ('questionnaire', 'user',)
    inlines = (MultiChoiceAnswerAdmin,)

    def get_urls(self):
        """ Extend the admin urls for the Answersheet admin model to be able to
            export the submitted sheets as a CSV file
        """
        urls = super(AnswerSheetAdmin, self).get_urls()
        admin_urls = patterns('',
                              url(
                                  r'^csv_export/$',
                                  self.admin_site.admin_view(self.csv_export),
                                  name='survey_answersheet_csv_export'
                              ))
        return admin_urls + urls

    def _get_max_answers(self):
        # get the maximum number of answers supplied in any questionnaire.
        result = 0
        qs = AnswerSheet.objects.values('id')
        if qs:
            qs = qs.annotate(answers=Count('multichoiceanswer'))
            qs = qs.order_by('-answers')
            result = list(qs)[0]['answers']
        return result

    def _translate_status(self, status):
        if status == constants.QUESTIONNAIRE_COMPLETED:
            return 'Completed'
        elif status == constants.QUESTIONNAIRE_INCOMPLETE:
            return 'Incomplete'
        elif status == constants.QUESTIONNAIRE_PENDING:
            return 'Pending'
        elif status == constants.QUESTIONNAIRE_REJECTED:
            return 'Rejected'
        return 'Unknown'

    def csv_export(self, request):
        """ Return a CSV document of the submitted survey answer sheets.
        """
        # generate a name for the CSV file
        now = datetime.datetime.now()
        filedate = "%04d%02d%02d" % (now.year, now.month, now.day)
        filename = "askMAMA_Survey_Answers_%s.csv" % (filedate)

        # determine the maximum answers to display per sheet
        max_answers = self._get_max_answers()

        # create and return the CSV file
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        # create the csv writer with the response as the output file
        writer = UnicodeWriter(response)

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
                    self._translate_status(sheet.get_status()),
                    "%s" % sheet.calculate_score()
                    ]
            for answer in sheet.multichoiceanswer_set.all():
                data.append(answer.question.question_text)
                data.append(answer.chosen_option.option_text)
            writer.writerow(data)

        return response

admin.site.register(AnswerSheet, AnswerSheetAdmin)


class QuestionnaireHolodeckKeysAdmin(admin.ModelAdmin):
    list_display = ('questionnaire', 'metric', 'holodeck_key',)
    raw_id_fields = ('questionnaire',)

admin.site.register(QuestionnaireHolodeckKeys, QuestionnaireHolodeckKeysAdmin)
