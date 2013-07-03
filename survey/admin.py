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

admin.site.register(AnswerSheet, AnswerSheetAdmin)


class QuestionnaireHolodeckKeysAdmin(admin.ModelAdmin):
    list_display = ('questionnaire', 'metric', 'holodeck_key',)
    raw_id_fields = ('questionnaire',)

admin.site.register(QuestionnaireHolodeckKeys, QuestionnaireHolodeckKeysAdmin)
