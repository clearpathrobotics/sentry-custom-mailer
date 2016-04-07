# Proprietary copyright: Clearpath Robotics, Confidential
#
# @author    Kieran Broekhoven <kbroekhoven@clearpathrobotics.com>
# @copyright (c) 2016, Clearpath Robotics, Inc., All rights reserved.

from __future__ import absolute_import

import logging

from django.conf import settings
from django.utils.encoding import force_text
from sentry.plugins.sentry_mail.models import MailPlugin
from django import forms
from multi_email_field.forms import MultiEmailField, MultiEmailWidget
from sentry.utils.email import MessageBuilder

import sentry_mailer

NOTSET = object()

logger = logging.getLogger(__name__)


class AddEmailForm(forms.Form):
    emails = MultiEmailField(widget=MultiEmailWidget())


class SentryMailer(MailPlugin):
    title = "Mailer"
    conf_key = 'mailer'
    conf_title = "Mailer"
    slug = 'mailer'
    version = sentry_mailer.VERSION

    author = "Kieran Broekhoven"
    author_url = "https://bitbucket.org/clearpathrobotics/sentry-mailer"

    project_default_enabled = True
    project_conf_form = AddEmailForm
    subject_prefix = settings.EMAIL_SUBJECT_PREFIX

    def get_send_to(self, project=None):
        """
        Returns a list of email addresses for the users that should be
        notified of alerts.
        """
        return self.get_option('emails', project) or []

    def _build_message(self, subject, template=None, html_template=None,
                       body=None, project=None, group=None, headers=None,
                       context=None):
        send_to = self.get_send_to(project)
        if not send_to:
            logger.debug('Skipping message rendering, no users to send to.')
            return
 
        subject_prefix = self.get_option('subject_prefix', project) or \
                self.subject_prefix
        subject_prefix = force_text(subject_prefix)
        subject = force_text(subject)

        msg = MessageBuilder(
            subject='%s%s' % (subject_prefix, subject),
            template=template,
            html_template=html_template,
            body=body,
            headers=headers,
            context=context,
            reference=group,
        )

        msg._send_to = set(send_to)

        return msg
        
# Legacy compatibility
MailProcessor = SentryMailer

