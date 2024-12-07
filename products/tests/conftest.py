import pytest


@pytest.fixture(autouse=True)
def configure_rest_framework_settings(settings):
    # Preserve existing settings
    settings.REST_FRAMEWORK = {
        **settings.REST_FRAMEWORK,
        # Override throttling settings for tests
        "DEFAULT_THROTTLE_CLASSES": [],
        "DEFAULT_THROTTLE_RATES": {},
    }
