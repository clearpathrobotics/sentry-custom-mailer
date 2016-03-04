"""
sentry.plugins.sentry_mail.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2014 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from __future__ import absolute_import

import logging

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from sentry.plugins import register
from sentry.plugins.bases.notify import NotificationPlugin
from sentry.utils.email import MessageBuilder, group_id_to_email
from sentry.utils.http import absolute_uri
from django import forms
from multi_email_field.forms import MultiEmailField, MultiEmailWidget

from sentry.plugins import sentry_mailer

NOTSET = object()

logger = logging.getLogger(__name__)


class AddEmailForm(forms.Form):
    emails = MultiEmailField(widget=MultiEmailWidget())


class SentryMailer(NotificationPlugin):
    title = "Mailer"
    conf_key = 'mailer'
    conf_title = "Mailer"
    slug = 'mailer'
    version = sentry_mailer.VERSION

    author = "Kieran Broekhoven"
    author_url = ""

    project_default_enabled = True
    project_conf_form = AddEmailForm
    subject_prefix = settings.EMAIL_SUBJECT_PREFIX

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

    def _send_mail(self, *args, **kwargs):
        message = self._build_message(*args, **kwargs)
        if message is not None:
            return message.send()

    def send_test_mail(self, project=None):
        self._send_mail(
            subject='Test Email',
            body='This email was requested as a test of Sentry\'s outgoing'
                 'email',
            project=project,
        )

    def get_notification_settings_url(self):
        return absolute_uri(reverse('sentry-account-settings-notifications'))

    def get_project_url(self, project):
        return absolute_uri(reverse('sentry-stream', args=[
            project.organization.slug,
            project.slug,
        ]))

    def is_configured(self, project, **kwargs):
        # Nothing to configure here
        return True

    def should_notify(self, group, event):
        send_to = self.get_sendable_users(group.project)
        if not send_to:
            return False

        return super(SentryMailer, self).should_notify(group, event)

    def get_send_to(self, project=None):
        """
        Returns a list of email addresses for the users that should be
        notified of alerts.
        """
        send_to_list = []

        for email in self.get_option('emails', project):
            send_to_list.append(email)

        return send_to_list

    def notify(self, notification):
        event = notification.event
        group = event.group
        project = group.project
        org = group.organization

        subject = group.get_email_subject()

        link = group.get_absolute_url()

        template = 'sentry/emails/error.txt'
        html_template = 'sentry/emails/error.html'

        rules = []
        for rule in notification.rules:
            rule_link = reverse('sentry-edit-project-rule', args=[
                org.slug, project.slug, rule.id
            ])
            rules.append((rule.label, rule_link))

        enhanced_privacy = org.flags.enhanced_privacy

        context = {
            'project_label': project.get_full_name(),
            'group': group,
            'event': event,
            'link': link,
            'rules': rules,
            'enhanced_privacy': enhanced_privacy,
        }

        # if the organization has enabled enhanced privacy controls we dont
        # send data which may show PII or source code
        if not enhanced_privacy:
            interface_list = []
            for interface in event.interfaces.itervalues():
                body = interface.to_email_html(event)
                if not body:
                    continue
                text_body = interface.to_string(event)
                interface_list.append(
                    (interface.get_title(), mark_safe(body), text_body)
                )

            context.update({
                'tags': event.get_tags(),
                'interfaces': interface_list,
            })

        headers = {
            'X-Sentry-Logger': group.logger,
            'X-Sentry-Logger-Level': group.get_level_display(),
            'X-Sentry-Team': project.team.name,
            'X-Sentry-Project': project.name,
            'X-Sentry-Reply-To': group_id_to_email(group.id),
        }

        self._send_mail(
            subject=subject,
            template=template,
            html_template=html_template,
            project=project,
            group=group,
            headers=headers,
            context=context,
        )
   
# Legacy compatibility
MailProcessor = SentryMailer

register(SentryMailer)
