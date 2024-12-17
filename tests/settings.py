INSTALLED_APPS = ["django_better_azure_communication_email"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

MIDDLEWARE_CLASSES = (
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
)

ROOT_URLCONF = ""

SECRET_KEY = "not-secret"

AZURE_COMMUNICATION_CONNECTION_STRING = (
    "DefaultEndpointsProtocol=https;" "AccountName=2321;" "AccountKey=dfsw23"
)
AZURE_TENANT_ID = "2352"
AZURE_CLIENT_ID = "3421"
AZURE_CLIENT_SECRET = "test-secret"
AZURE_COMMUNICATION_ENDPOINT = "https://endpoint-not-used.com/"
AZURE_KEY_CREDENTIAL = "Naaarh"
AZURE_COMMUNICATION_TRACKING_DISABLED = False
