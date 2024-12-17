from django.conf import settings
from django.test import TestCase, override_settings


_connection_str = (
    "DefaultEndpointsProtocol=https;",
    "AccountName=djangoace;",
    "AccountKey=1234",
)
_tenant_id = "1234"
_client_id = "1234"
_client_secret = "1234"
_endpoint = "https://endpoint"
_key_credential = "1234"


class TestSettings(TestCase):
    @override_settings(AZURE_COMMUNICATION_CONNECTION_STRING=_connection_str)
    def test_connection_string(self):
        self.assertEqual(
            settings.AZURE_COMMUNICATION_CONNECTION_STRING, _connection_str
        )

    @override_settings(AZURE_TENANT_ID=_tenant_id)
    def test_tenant_id(self):
        self.assertEqual(settings.AZURE_TENANT_ID, _tenant_id)

    @override_settings(AZURE_CLIENT_ID=_client_id)
    def test_client_id(self):
        self.assertEqual(settings.AZURE_CLIENT_ID, _client_id)

    @override_settings(AZURE_CLIENT_SECRET=_client_secret)
    def test_client_secret(self):
        self.assertEqual(settings.AZURE_CLIENT_SECRET, _client_secret)

    @override_settings(AZURE_COMMUNICATION_ENDPOINT=_endpoint)
    def test_endpoint(self):
        self.assertEqual(settings.AZURE_COMMUNICATION_ENDPOINT, _endpoint)

    @override_settings(AZURE_KEY_CREDENTIAL=_key_credential)
    def test_key_credential(self):
        self.assertEqual(settings.AZURE_KEY_CREDENTIAL, _key_credential)

    @override_settings(AZURE_COMMUNICATION_TRACKING_DISABLED=True)
    def test_tracking_disabled_1(self):
        self.assertEqual(settings.AZURE_COMMUNICATION_TRACKING_DISABLED, True)

    @override_settings(AZURE_COMMUNICATION_TRACKING_DISABLED=False)
    def test_tracking_disabled_2(self):
        self.assertEqual(settings.AZURE_COMMUNICATION_TRACKING_DISABLED, False)
