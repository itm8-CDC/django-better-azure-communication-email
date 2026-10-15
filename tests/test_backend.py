import base64
import unittest
import warnings
from unittest import mock

import django
from django.conf import settings
from django.core import mail
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.test import TestCase, override_settings

from django_better_azure_communication_email import EmailBackend


class EmailClientStub:
    """Behaves like `azure.communication.email.EmailClient`."""

    def __init__(self):
        self.messages = []

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):  # noqa
        pass

    def begin_send(self, message):
        self.messages.append(message)


class TestEmailBackend(TestCase):
    """backend.ACEmailBackend()"""

    def setUp(self) -> None:
        self.backend = EmailBackend()
        self.client = self.backend._client = EmailClientStub()

    def test_fail_silent(self):
        backend = EmailBackend(fail_silently=True)
        backend.open()

    def test_fail_not_silent(self):
        backend = EmailBackend(fail_silently=False)
        with self.assertRaises(Exception):
            backend.open()

    def test_convert_plain_email_message(self):
        message = EmailMessage(
            subject="Subject",
            body="plain text",
            from_email="Support <support@company.com>",
            to=["Foo <foo@company.com>"],
            cc=["Bar <bar@company.com>", "baz@company.com"],
            bcc=["alice@company.com", "bob@company.com"],
            reply_to=["Reply <reply@company.com>"],
            headers={"X-Header": "value"},
        )

        conv_message = self.backend.convert_message(message)

        self.assertEqual(conv_message["content"]["subject"], message.subject)
        self.assertEqual(conv_message["content"]["plainText"], message.body)
        self.assertFalse("html" in conv_message["content"])
        self.assertEqual(conv_message["senderAddress"], "support@company.com")
        self.assertEqual(
            conv_message["recipients"]["to"],
            [
                {"displayName": "Foo", "address": "foo@company.com"},
            ],
        )
        self.assertEqual(
            conv_message["recipients"]["cc"],
            [
                {"displayName": "Bar", "address": "bar@company.com"},
                {"displayName": "", "address": "baz@company.com"},
            ],
        )
        self.assertEqual(
            conv_message["recipients"]["bcc"],
            [
                {"displayName": "", "address": "alice@company.com"},
                {"displayName": "", "address": "bob@company.com"},
            ],
        )
        self.assertEqual(
            conv_message["replyTo"],
            [
                {"displayName": "Reply", "address": "reply@company.com"},
            ],
        )
        self.assertEqual(conv_message["headers"], {"X-Header": "value"})
        self.assertFalse("attachments" in conv_message)

    def test_convert_html_email_message(self):
        message = EmailMultiAlternatives(
            subject="Subject",
            body="plain text",
            from_email="Support <support@company.com>",
            to=["Foo <foo@company.com>"],
        )
        message.attach_alternative("<p>html</p>", "text/html")

        conv_message = self.backend.convert_message(message)

        self.assertEqual(conv_message["content"]["subject"], message.subject)
        self.assertEqual(conv_message["content"]["plainText"], message.body)
        self.assertEqual(conv_message["content"]["html"], "<p>html</p>")
        self.assertEqual(conv_message["senderAddress"], "support@company.com")
        self.assertEqual(
            conv_message["recipients"]["to"],
            [
                {"displayName": "Foo", "address": "foo@company.com"},
            ],
        )
        self.assertFalse("cc" in conv_message)
        self.assertFalse("bcc" in conv_message)
        self.assertFalse("replyTo" in conv_message)
        self.assertFalse("headers" in conv_message)
        self.assertFalse("attachments" in conv_message)

    def test_convert_email_message_with_attachments(self):
        message = EmailMessage(
            subject="Subject",
            body="plain text",
            from_email="Support <support@company.com>",
            to=["Foo <foo@company.com>"],
        )
        message.attach("file.txt", "content", "text/plain")

        conv_message = self.backend.convert_message(message)

        self.assertEqual(conv_message["content"]["subject"], message.subject)
        self.assertEqual(conv_message["content"]["plainText"], message.body)
        self.assertFalse("html" in conv_message["content"])
        self.assertEqual(conv_message["senderAddress"], "support@company.com")
        self.assertEqual(
            conv_message["recipients"]["to"],
            [
                {"displayName": "Foo", "address": "foo@company.com"},
            ],
        )
        self.assertFalse("cc" in conv_message)
        self.assertFalse("bcc" in conv_message)
        self.assertFalse("replyTo" in conv_message)
        self.assertFalse("headers" in conv_message)
        self.assertEqual(len(conv_message["attachments"]), 1)
        self.assertDictEqual(
            conv_message["attachments"][0],
            {
                "name": "file.txt",
                "contentType": "text/plain",
                "contentInBase64": base64.b64encode(b"content").decode(),
            },
        )

    def test_send_message(self):
        message = EmailMessage(
            subject="Subject",
            body="plain text",
            from_email="Support <support@company.com>",
            to=["Foo <foo@company.com>"],
        )
        self.backend.send_messages([message])

        self.assertEqual(len(self.client.messages), 1)
        self.assertDictEqual(
            self.client.messages[0],
            {
                "senderAddress": "support@company.com",
                "recipients": {
                    "to": [
                        {"displayName": "Foo", "address": "foo@company.com"},
                    ],
                },
                "content": {
                    "subject": "Subject",
                    "plainText": "plain text",
                },
            },
        )
        self.assertIsNone(self.backend._client)


_BACKEND_PATH = "django_better_azure_communication_email.EmailBackend"
_HAS_MAILERS = django.VERSION >= (6, 1)
_OPTION_CONN_STR = "endpoint=https://option.com/;accesskey=a"


def _make_message(**kwargs):
    return EmailMessage(
        subject="Subject",
        body="plain text",
        from_email="Support <support@company.com>",
        to=["Foo <foo@company.com>"],
        **kwargs,
    )


class TestEmailBackendSetting(TestCase):
    """Configuration through the EMAIL_BACKEND setting."""

    @override_settings(EMAIL_BACKEND=_BACKEND_PATH)
    def test_get_connection(self):
        with warnings.catch_warnings():
            # get_connection() is deprecated in Django 6.1+.
            warnings.simplefilter("ignore")
            backend = mail.get_connection()

        self.assertIsInstance(backend, EmailBackend)
        self.assertFalse(backend.fail_silently)

    @override_settings(EMAIL_BACKEND=_BACKEND_PATH)
    def test_get_connection_fail_silently(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            backend = mail.get_connection(fail_silently=True)

        self.assertIsInstance(backend, EmailBackend)
        self.assertTrue(backend.fail_silently)

    @override_settings(EMAIL_BACKEND=_BACKEND_PATH)
    def test_send_mail(self):
        client = EmailClientStub()
        with mock.patch(
            "django_better_azure_communication_email.backend.EmailClient"
        ) as email_client:
            email_client.from_connection_string.return_value = client
            sent = mail.send_mail(
                "Subject",
                "plain text",
                "support@company.com",
                ["foo@company.com"],
            )

        self.assertEqual(sent, 1)
        self.assertEqual(len(client.messages), 1)

    def test_no_deprecation_warnings(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            backend = EmailBackend()
            self.assertFalse(backend.fail_silently)
            backend = EmailBackend(fail_silently=True)
            self.assertTrue(backend.fail_silently)

    @override_settings(AZURE_COMMUNICATION_TRACKING_DISABLED=True)
    def test_tracking_disabled_option(self):
        backend = EmailBackend(tracking_disabled=True)
        conv_message = backend.convert_message(_make_message())
        self.assertTrue(conv_message["userEngagementTrackingDisabled"])

        backend = EmailBackend(tracking_disabled=False)
        conv_message = backend.convert_message(_make_message())
        self.assertNotIn("userEngagementTrackingDisabled", conv_message)


@unittest.skipUnless(_HAS_MAILERS, "MAILERS requires Django 6.1+")
@override_settings(
    MAILERS={
        "default": {"BACKEND": _BACKEND_PATH},
        "azure": {
            "BACKEND": _BACKEND_PATH,
            "OPTIONS": {
                "connection_string": _OPTION_CONN_STR,
                "tracking_disabled": True,
            },
        },
        "silent": {
            "BACKEND": _BACKEND_PATH,
            "OPTIONS": {"fail_silently": True},
        },
        "invalid": {
            "BACKEND": _BACKEND_PATH,
            "OPTIONS": {"unknown_option": True},
        },
    }
)
class TestMailersSetting(TestCase):
    """Configuration through the MAILERS setting (Django 6.1+)."""

    def test_default_mailer(self):
        backend = mail.mailers.default

        self.assertIsInstance(backend, EmailBackend)
        self.assertEqual(backend.alias, "default")
        self.assertFalse(backend.fail_silently)
        # Falls back to the AZURE_* settings.
        self.assertEqual(
            backend._connection_string,
            settings.AZURE_COMMUNICATION_CONNECTION_STRING,
        )

    def test_mailer_options(self):
        backend = mail.mailers["azure"]

        self.assertIsInstance(backend, EmailBackend)
        self.assertEqual(backend.alias, "azure")
        self.assertEqual(
            backend._connection_string,
            _OPTION_CONN_STR,
        )
        self.assertTrue(backend._tracking_disabled)

    def test_mailer_fail_silently_option(self):
        backend = mail.mailers["silent"]
        self.assertTrue(backend.fail_silently)

    def test_mailer_unknown_option(self):
        with self.assertRaises(mail.InvalidMailer):
            mail.mailers["invalid"]

    def test_send_mail_using(self):
        client = EmailClientStub()
        with mock.patch(
            "django_better_azure_communication_email.backend.EmailClient"
        ) as email_client:
            email_client.from_connection_string.return_value = client
            sent = mail.send_mail(
                "Subject",
                "plain text",
                "support@company.com",
                ["foo@company.com"],
                using="azure",
            )

        from_conn_str = email_client.from_connection_string
        from_conn_str.assert_called_once_with(_OPTION_CONN_STR)
        self.assertEqual(sent, 1)
        self.assertEqual(len(client.messages), 1)
        self.assertTrue(client.messages[0]["userEngagementTrackingDisabled"])

    def test_email_message_send_using(self):
        client = EmailClientStub()
        with mock.patch(
            "django_better_azure_communication_email.backend.EmailClient"
        ) as email_client:
            email_client.from_connection_string.return_value = client
            sent = _make_message().send(using="azure")

        self.assertEqual(sent, 1)
        self.assertEqual(len(client.messages), 1)

    def test_send_mail_using_fail_silently_not_supported(self):
        # Django does not support fail_silently together with MAILERS.
        with self.assertRaises(TypeError):
            mail.send_mail(
                "Subject",
                "plain text",
                "support@company.com",
                ["foo@company.com"],
                fail_silently=True,
                using="azure",
            )
