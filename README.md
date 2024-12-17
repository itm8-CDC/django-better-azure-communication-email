[![codecov](https://codecov.io/gh/itm8-CDC/django-better-azure-communication-email/graph/badge.svg?token=L167GIRS20)](https://codecov.io/gh/itm8-CDC/django-better-azure-communication-email)

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
