from setuptools import setup

install_requires = ['django==1.6', 'django-multi-email-field', 'sentry']

setup(
    name='sentry-mailer',
    version='1.0.0',
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
)

