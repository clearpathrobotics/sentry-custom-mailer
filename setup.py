#!/usr/bin/env python
from setuptools import setup, find_packages

install_requires = ['django', 'django-multi-email-field', 'sentry']

setup(
    name='sentry-mailer',
    version='1.0.1',
    author="Kieran Broekhoven",
    author_email="kbroekhoven@clearpathrobotics.com",
    description="A sentry plugin to specify recipients of notification emails",
    long_description=open('README.md').read(),
    install_requires=install_requires,
    entry_points={
        'sentry.plugins': [
            'mailer = sentry_mailer.plugin:SentryMailer'
        ],
        'sentry.apps': [
            'mailer = sentry_mailer'
        ],
    },
    packages=find_packages(),
)

