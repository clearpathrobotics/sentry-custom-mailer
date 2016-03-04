# sentry-mailer
A sentry plugin that allows you to specify certain recipients of notification for the given project.

## Configuration
Place the directory `sentry_mailer/sentry_mailer` from this in `sentry/plugins/` on the Sentry server. 

Open `sentry/conf/server.py`, locate the list `INSTALLED_APPS` and add `sentry.plugins.sentry_mailer`.

## Usage
In Sentry project settings, go to the configuration settings for "sentry\_mailer" and enter all email addresses that should receive notifications for that project. 
