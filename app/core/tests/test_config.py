import os
import warnings
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from yarl import URL

from app.core.config import MYSQL_SCHEME
from app.core.config import Settings
from app.core.config import parse_cors


# Constants for magic values
DEFAULT_MYSQL_PORT: int = 3306
DEFAULT_SMTP_PORT: int = 587


@pytest.fixture
def base_settings() -> dict[str, str]:
    """Fixture providing base settings for required fields."""
    return {
        "PROJECT_NAME": "TestProject",
        "STACK_NAME": "TestStack",
        "MYSQL_SERVER": "localhost",
        "MYSQL_ROOT_PASSWORD": "rootpass",
        "MYSQL_USER": "testuser",
        "MYSQL_PASSWORD": "testpass",
        "FIRST_SUPERUSER_PASSWORD": "securepassword",
        "STREEM_USERNAME": "streemuser",
        "STREEM_PASSWORD": "streempass",
        "NORDPOOL_USERNAME": "nord_pool_user",
        "NORDPOOL_PASSWORD": "nord_pool_pass",
        "EMAIL_SUPERUSER_EMAIL": "test@example.com",
    }


def test_mysql_scheme() -> None:
    """Test the MYSQL_SCHEME constant."""
    assert MYSQL_SCHEME == "mysql+pymysql"


def test_default_settings(base_settings: dict[str, str]) -> None:
    """Test default settings initialization."""
    settings = Settings(**base_settings)
    assert settings.API_V1_STR == "/api/v1"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60 * 24 * 8
    assert settings.FRONTEND_HOST == "http://localhost:5173"
    assert settings.ENVIRONMENT == "local"
    assert settings.MYSQL_PORT == DEFAULT_MYSQL_PORT
    assert settings.EMAIL_SUPERUSER_EMAIL == "test@example.com"
    assert settings.SMTP_PORT == DEFAULT_SMTP_PORT
    assert settings.SMTP_TLS is True
    assert settings.SMTP_SSL is False


def test_computed_db_uri(base_settings: dict[str, str]) -> None:
    """Test db_uri computed field."""
    base_settings.update(
        {
            "MYSQL_DATABASE": "testdb",
            "MYSQL_PORT": DEFAULT_MYSQL_PORT,
        },
    )
    settings = Settings(**base_settings)
    expected_uri = URL(f"{MYSQL_SCHEME}://testuser:testpass@localhost:3306/testdb")
    assert settings.db_uri == expected_uri


def test_computed_db_uri_test(base_settings: dict[str, str]) -> None:
    """Test db_uri_test computed field."""
    base_settings.update(
        {
            "MYSQL_DATABASE_TEST": "testdb_test",
            "MYSQL_PORT": DEFAULT_MYSQL_PORT,
        },
    )
    settings = Settings(**base_settings)
    expected_uri = URL(f"{MYSQL_SCHEME}://testuser:testpass@localhost:3306/testdb_test")
    assert settings.db_uri_test == expected_uri


def test_cors_origins_parsing(base_settings: dict[str, str]) -> None:
    """Test CORS origins parsing with different input formats."""
    # Test comma-separated string
    base_settings["BACKEND_CORS_ORIGINS"] = "http://example.com,http://api.example.com"
    settings = Settings(**base_settings)
    assert settings.all_cors_origins == [
        "http://example.com",
        "http://api.example.com",
        "http://localhost:5173",
    ]

    # Test list input
    base_settings["BACKEND_CORS_ORIGINS"] = ["http://test.com", "https://secure.com"]
    settings = Settings(**base_settings)
    assert settings.all_cors_origins == [
        "http://test.com",
        "https://secure.com",
        "http://localhost:5173",
    ]

    # Test empty string
    base_settings["BACKEND_CORS_ORIGINS"] = ""
    settings = Settings(**base_settings)
    assert settings.all_cors_origins == ["http://localhost:5173"]


def test_parse_cors_invalid_input() -> None:
    """Test parse_cors with invalid input."""
    with pytest.raises(ValueError, match="123"):
        parse_cors(123)  # Invalid type


def test_emails_enabled(base_settings: dict[str, str]) -> None:
    """Test emails_enabled computed field."""
    # Emails disabled when SMTP_HOST or EMAILS_FROM_EMAIL is missing
    settings = Settings(**base_settings)
    assert settings.emails_enabled is False

    # Emails enabled when both are provided
    base_settings.update(
        {
            "SMTP_HOST": "smtp.example.com",
            "EMAILS_FROM_EMAIL": "from@example.com",
        },
    )
    settings = Settings(**base_settings)
    assert settings.emails_enabled is True


def test_default_emails_from_name(base_settings: dict[str, str]) -> None:
    """Test default EMAILS_FROM_NAME is set to PROJECT_NAME."""
    with patch.dict(os.environ, {}, clear=True), patch("dotenv.load_dotenv", return_value=None):
        settings = Settings(**base_settings)
        assert settings.PROJECT_NAME == "TestProject"  # Verify fixture value
        assert settings.EMAILS_FROM_NAME == "TestProject"  # Verify default EMAILS_FROM_NAME

        # Test with explicit EMAILS_FROM_NAME
        base_settings["EMAILS_FROM_NAME"] = "Custom Name"
        settings = Settings(**base_settings)
        assert settings.EMAILS_FROM_NAME == "Custom Name"


def test_secret_key_warning_local(base_settings: dict[str, str]) -> None:
    """Test warning for default secret in local environment."""
    base_settings["SECRET_KEY"] = "changethis"
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        settings = Settings(**base_settings)
        assert len(w) >= 1
        assert "SECRET_KEY" in str(w[-1].message)
        assert settings.SECRET_KEY == "changethis"


def test_secret_key_error_non_local(base_settings: dict[str, str]) -> None:
    """Test error for default secret in non-local environment."""
    base_settings.update(
        {
            "SECRET_KEY": "changethis",
            "ENVIRONMENT": "production",
        },
    )
    with pytest.raises(ValueError, match="SECRET_KEY"):
        Settings(**base_settings)


def test_mysql_password_warning_local(base_settings: dict[str, str]) -> None:
    """Test warning for default MySQL password in local environment."""
    base_settings["MYSQL_PASSWORD"] = "changethis"
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        settings = Settings(**base_settings)
        assert len(w) >= 1
        assert "MYSQL_PASSWORD" in str(w[-1].message)
        assert settings.MYSQL_PASSWORD == "changethis"


def test_mysql_password_error_non_local(base_settings: dict[str, str]) -> None:
    """Test error for default MySQL password in non-local environment."""
    base_settings.update(
        {
            "MYSQL_PASSWORD": "changethis",
            "ENVIRONMENT": "production",
        },
    )
    with pytest.raises(ValueError, match="MYSQL_PASSWORD"):
        Settings(**base_settings)


def test_missing_required_fields() -> None:
    """Test validation error for missing required fields."""
    with patch.dict(os.environ, {}, clear=True), patch("dotenv.load_dotenv", return_value=None):
        with pytest.raises(ValidationError) as exc_info:
            Settings()
        assert "PROJECT_NAME" in str(exc_info.value)
        assert "STACK_NAME" in str(exc_info.value)
        assert "MYSQL_ROOT_PASSWORD" in str(exc_info.value)


def test_streem_credentials(base_settings: dict[str, str]) -> None:
    """Test Streem API credentials."""
    settings = Settings(**base_settings)
    assert settings.STREEM_USERNAME == "streemuser"
    assert settings.STREEM_PASSWORD == "streempass"


def test_nordpool_credentials(base_settings: dict[str, str]) -> None:
    """Test Nordpool API credentials."""
    settings = Settings(**base_settings)
    assert settings.NORDPOOL_USERNAME == "nord_pool_user"
    assert settings.NORDPOOL_PASSWORD == "nord_pool_pass"


def test_sentry_dsn_none(base_settings: dict[str, str]) -> None:
    """Test SENTRY_DSN default value."""
    settings = Settings(**base_settings)
    assert settings.SENTRY_DSN is None


def test_sentry_dsn_valid(base_settings: dict[str, str]) -> None:
    """Test SENTRY_DSN with a valid URL."""
    base_settings["SENTRY_DSN"] = "https://example@sentry.io/123"
    settings = Settings(**base_settings)
    assert str(settings.SENTRY_DSN) == "https://example@sentry.io/123"


def test_email_superuser_email(base_settings: dict[str, str]) -> None:
    """Test EMAIL_SUPERUSER_EMAIL default value."""
    settings = Settings(**base_settings)
    assert settings.EMAIL_SUPERUSER_EMAIL == "test@example.com"

    # Test with custom EMAIL_SUPERUSER_EMAIL
    base_settings["EMAIL_SUPERUSER_EMAIL"] = "custom@example.com"
    settings = Settings(**base_settings)
    assert settings.EMAIL_SUPERUSER_EMAIL == "custom@example.com"
