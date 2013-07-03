""" Cron-able script to push statistics to holodeck
"""
import datetime
from urllib2 import HTTPError
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Count
from django.contrib.auth.models import User

from photon import Client
from survey import constants
from survey.models import Questionnaire, QuestionnaireHolodeckKeys

logger = logging.getLogger('survey_holodeck_push')


class Command(BaseCommand):
    help = "Pushes askMAMA survey statistics to Holodeck dashboard."

    def handle(self, *args, **options):
        users = User.objects.filter(is_active=True)
        questionnaires = Questionnaire.objects.filter(active=True)

        client = Client(server=settings.HOLODECK_URL)
        now = datetime.datetime.now()

        for questionnaire in questionnaires:
            # check if we have holodeck keys for the questionnaire
            pending_key = self._get_holodeck_key(
                questionnaire,
                constants.QUESTIONNAIRE_PENDING)
            completed_key = self._get_holodeck_key(
                questionnaire,
                constants.QUESTIONNAIRE_COMPLETED)
            incomplete_key = self._get_holodeck_key(
                questionnaire,
                constants.QUESTIONNAIRE_INCOMPLETE)

            # collect the stats for the questionnaire
            if pending_key or completed_key or incomplete_key:
                pending = incomplete = completed = 0
                for user in users:
                    status = questionnaire.get_status(user)
                    if status == constants.QUESTIONNAIRE_PENDING:
                        pending += 1
                    elif status == constants.QUESTIONNAIRE_INCOMPLETE:
                        incomplete += 1
                    elif status == constants.QUESTIONNAIRE_COMPLETED:
                        completed += 1

                # send the pending stats to holodeck
                if pending_key:
                    try:
                        client.send(
                            samples=(("Total", pending),),
                            api_key=pending_key,
                            timestamp=now
                        )
                    except HTTPError:
                        logger.error("Could not connect to holodeck service")

                # send the incomplete stats to holodeck
                if incomplete_key:
                    try:
                        client.send(
                            samples=(("Total", incomplete),),
                            api_key=incomplete_key,
                            timestamp=now
                        )
                    except HTTPError:
                        logger.error("Could not connect to holodeck service")

                # send the complete stats to holodeck
                if completed_key:
                    try:
                        client.send(
                            samples=(("Total", completed),),
                            api_key=completed_key,
                            timestamp=now
                        )
                    except HTTPError:
                        logger.error("Could not connect to holodeck service")

    def _get_holodeck_key(self, questionnaire, metric):
        """ Retrieve the specified holodeck key for the qeustionnaire
        """
        try:
            key = QuestionnaireHolodeckKeys.objects.get(
                questionnaire=questionnaire,
                metric=metric)
            return key.holodeck_key
        except QuestionnaireHolodeckKeys.DoesNotExist:
            logger.error("Holodeck API key for survey metric %s missing",
                         metric)
