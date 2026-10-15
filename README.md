[![codecov](https://codecov.io/gh/itm8-CDC/django-better-azure-communication-email/graph/badge.svg?token=L167GIRS20)](https://codecov.io/gh/itm8-CDC/django-better-azure-communication-email)
[![PyPI - Version](https://img.shields.io/pypi/v/django-better-azure-communication-email)](https://pypi.org/project/django-better-azure-communication-email/)

# Django Better Azure Communication Email
This is a fork from: https://github.com/retech-us/django-azure-communication-email

A Django email backend for Azure Communication Email service.

## Installation
Run the following on your system:

    pip install django-better-azure-communication-email

Then, add these settings to your Django `settings.py`:

    EMAIL_BACKEND = 'django_better_azure_communication_email.EmailBackend'

    AZURE_COMMUNICATION_CONNECTION_STRING = '...'
    # OR
    AZURE_KEY_CREDENTIAL = '...'
    AZURE_COMMUNICATION_ENDPOINT = '...'

If you prefer to use Azure Active Directory authentication, you can use the
following `settings.py` instead:

    EMAIL_BACKEND = 'django_better_azure_communication_email.EmailBackend'

    AZURE_COMMUNICATION_ENDPOINT = '...'

    # Note: make sure to set the following environment variables:
    # AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET

Now, when you use `django.core.mail.send_mail`, Azure Communication Email
service will send the messages by default.

## Using `MAILERS` (Django 6.1+)
Django 6.1 introduced the [`MAILERS`](https://docs.djangoproject.com/en/6.1/topics/email/)
setting, which deprecates `EMAIL_BACKEND`. Both are supported. With `MAILERS`,
the backend can be configured through `OPTIONS`:

    MAILERS = {
        "default": {
            "BACKEND": "django_better_azure_communication_email.EmailBackend",
            "OPTIONS": {
                "connection_string": "...",
            },
        },
    }

Available `OPTIONS` (each one falls back to the matching setting when not
given):

| Option              | Fallback setting                         |
|---------------------|------------------------------------------|
| `connection_string` | `AZURE_COMMUNICATION_CONNECTION_STRING`  |
| `endpoint`          | `AZURE_COMMUNICATION_ENDPOINT`           |
| `key_credential`    | `AZURE_KEY_CREDENTIAL`                   |
| `tenant_id`         | `AZURE_TENANT_ID`                        |
| `client_id`         | `AZURE_CLIENT_ID`                        |
| `client_secret`     | `AZURE_CLIENT_SECRET`                    |
| `tracking_disabled` | `AZURE_COMMUNICATION_TRACKING_DISABLED`  |
| `fail_silently`     | (defaults to `False`)                    |

Note: Django does not allow the `fail_silently` argument together with
`using` (e.g. `send_mail(..., using="default", fail_silently=True)` raises a
`TypeError`). If you need a mailer that fails silently, set
`"fail_silently": True` in its `OPTIONS` instead.
