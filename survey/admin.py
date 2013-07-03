import csv
import datetime

from django.contrib import admin
from django.conf.urls.defaults import patterns, url
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

    def csv_export(self, request):
        """ Return a CSV document of the submitted survey answer sheets.
        """

admin.site.register(AnswerSheet, AnswerSheetAdmin)


class QuestionnaireHolodeckKeysAdmin(admin.ModelAdmin):
    list_display = ('questionnaire', 'metric', 'holodeck_key',)
    raw_id_fields = ('questionnaire',)

admin.site.register(QuestionnaireHolodeckKeys, QuestionnaireHolodeckKeysAdmin)
