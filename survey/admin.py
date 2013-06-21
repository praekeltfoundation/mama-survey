from django.contrib import admin

from survey.models import Questionnaire, MultiChoiceQuestion, MultiChoiceOption
from survey.models import AnswerSheet, MultiChoiceAnswer


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
    raw_id_fields = ('user',) 
    inlines = (MultiChoiceAnswerAdmin,)

admin.site.register(AnswerSheet, AnswerSheetAdmin)
