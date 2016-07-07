from django.db import models

from os import environ as env

from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import Context, Template

import requests
import json

pushbullet_api_url = "https://api.pushbullet.com/v2/pushes"
pushbullet_template = "Service {{ service.name }} {% if service.overall_status == service.PASSING_STATUS %}is back to normal{% else %}reporting {{ service.overall_status }} status{% endif %}: {{ scheme }}://{{ host }}{% url 'service' pk=service.id %}. {% if service.overall_status != service.PASSING_STATUS %}Checks failing: {% for check in service.all_failing_checks %}{% if check.check_category == 'Jenkins check' %}{% if check.last_result.error %} {{ check.name }} ({{ check.last_result.error|safe }}) {{jenkins_api}}job/{{ check.name }}/{{ check.last_result.job_number }}/console{% else %} {{ check.name }} {{jenkins_api}}/job/{{ check.name }}/{{check.last_result.job_number}}/console {% endif %}{% else %} {{ check.name }} {% if check.last_result.error %} ({{ check.last_result.error|safe }}){% endif %}{% endif %}{% endfor %}{% endif %}"

class PushbulletAlert(AlertPlugin):
    name = "Pushbullet"
    author = "Rich Shakespeare"

    def send_alert(self, service, users, duty_officers):
        alert = True
        users = list(users) + list(duty_officers)

        if service.overall_status == service.WARNING_STATUS:
            alert = False  # Don't alert at all for WARNING
        if service.overall_status == service.ERROR_STATUS:
            if service.old_overall_status in (service.ERROR_STATUS, service.ERROR_STATUS):
                alert = False  # Don't alert repeatedly for ERROR
        if service.overall_status == service.PASSING_STATUS:
            if service.old_overall_status == service.WARNING_STATUS:
                alert = False  # Don't alert for recovery from WARNING status

        # send one push to each configured pushbullet api key
        pushbullet_api_keys = [user_data.api_key for user_data in PushbulletAlertUserData.objects.filter(user__user__in=users)]
        for pushbullet_api_key in pushbullet_api_keys:
          context = Context({
              'service': service,
              'host': settings.WWW_HTTP_HOST,
              'scheme': settings.WWW_SCHEME,
              'alert': alert,
              'jenkins_api': settings.JENKINS_API,
          })
          message = Template(pushbullet_template).render(context)
          self._send_pushbullet_alert(pushbullet_api_key, title, message)

    def _send_pushbullet_alert(self, api_key, title, message):
        resp = requests.post(pushbullet_api_url, data=json.dumps({
            'title': title,
            'body': message,
            'type': note
          }), headers={
            'Access-Token: {}'.format(api_key),
            'Content-Type: application/json'
          })

class PushbulletAlertUserData(AlertPluginUserData):
    name = "Pushbullet Plugin"
    api_key = models.CharField(max_length=50, blank=True)

