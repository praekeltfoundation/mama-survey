# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'AnswerSheet', fields ['questionnaire']
        db.delete_unique('survey_answersheet', ['questionnaire_id'])


        # Changing field 'AnswerSheet.questionnaire'
        db.alter_column('survey_answersheet', 'questionnaire_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Questionnaire']))

    def backwards(self, orm):

        # Changing field 'AnswerSheet.questionnaire'
        db.alter_column('survey_answersheet', 'questionnaire_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['survey.Questionnaire'], unique=True))
        # Adding unique constraint on 'AnswerSheet', fields ['questionnaire']
        db.create_unique('survey_answersheet', ['questionnaire_id'])


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'survey.answersheet': {
            'Meta': {'ordering': "('user', 'date_created')", 'object_name': 'AnswerSheet'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'questionnaire': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Questionnaire']"}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'survey.multichoiceanswer': {
            'Meta': {'ordering': "('answer_sheet', 'question__question_order')", 'object_name': 'MultiChoiceAnswer'},
            'answer_sheet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.AnswerSheet']"}),
            'chosen_option': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['survey.MultiChoiceOption']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['survey.MultiChoiceQuestion']", 'unique': 'True'})
        },
        'survey.multichoiceoption': {
            'Meta': {'ordering': "('option_order',)", 'object_name': 'MultiChoiceOption'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_correct_option': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'option_order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'option_text': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.MultiChoiceQuestion']"})
        },
        'survey.multichoicequestion': {
            'Meta': {'ordering': "('question_order',)", 'object_name': 'MultiChoiceQuestion'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question_order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'question_text': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'questionnaire': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Questionnaire']"})
        },
        'survey.questionnaire': {
            'Meta': {'ordering': "('-date_created',)", 'object_name': 'Questionnaire'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'introduction_text': ('django.db.models.fields.TextField', [], {}),
            'thank_you_text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['survey']