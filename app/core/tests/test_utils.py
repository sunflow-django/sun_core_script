import logging
import warnings
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from app.core.utils import EnvFileNotFoundWarning
from app.core.utils import check_env_file
from app.core.utils import find_env_file


# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for testing."""
    return tmp_path


@pytest.fixture
def mock_path_is_file(mocker: MockerFixture) -> MagicMock:
    """Mock Path.is_file() for controlled testing."""
    return mocker.patch.object(Path, "is_file")


@pytest.fixture
def mock_path_exists(mocker: MockerFixture) -> MagicMock:
    """Mock Path.exists() for controlled testing."""
    return mocker.patch.object(Path, "exists")


@pytest.fixture
def mock_path_is_dir(mocker: MockerFixture) -> MagicMock:
    """Mock Path.is_dir() for controlled testing."""
    return mocker.patch.object(Path, "is_dir")


@pytest.fixture
def mock_logger(mocker: MockerFixture) -> MagicMock:
    """Mock logger to capture log messages."""
    return mocker.patch("app.core.utils.logger")


def test_check_env_file_exists(temp_dir: Path, mock_logger: MagicMock) -> None:
    """Test check_env_file when the file exists."""
    env_file = temp_dir / ".env"
    env_file.touch()  # Create an empty file
    assert check_env_file(env_file) is True
    mock_logger.debug.assert_called_with("Found .env file at %s", env_file)


def test_check_env_file_not_exists(temp_dir: Path) -> None:
    """Test check_env_file when the file does not exist."""
    env_file = temp_dir / ".env"
    assert check_env_file(env_file) is False


def test_check_env_file_permission_error(mock_path_is_file: MagicMock, mock_logger: MagicMock) -> None:
    """Test check_env_file when a PermissionError occurs."""
    mock_path_is_file.side_effect = PermissionError("Permission denied")
    env_file = Path("/fake/path/.env")
    with pytest.raises(PermissionError, match="Permission denied"):
        check_env_file(env_file)
    mock_logger.exception.assert_called_with("Permission denied accessing .env file %s", env_file)


def test_check_env_file_os_error(mock_path_is_file: MagicMock, mock_logger: MagicMock) -> None:
    """Test check_env_file when an OSError occurs."""
    mock_path_is_file.side_effect = OSError("OS error")
    env_file = Path("/fake/path/.env")
    with pytest.raises(OSError, match="OS error"):
        check_env_file(env_file)
    mock_logger.exception.assert_called_with("OS error accessing .env file %s", env_file)


def test_find_env_file_exists(temp_dir: Path, mock_logger: MagicMock) -> None:
    """Test find_env_file when the .env file exists in the start directory."""
    env_file = temp_dir / ".env"
    env_file.touch()  # Create an empty file
    result = find_env_file(temp_dir)
    assert result == env_file
    mock_logger.info.assert_called_with("Found .env file at %s", env_file)


def test_find_env_file_in_parent(temp_dir: Path, mock_logger: MagicMock) -> None:
    """Test find_env_file when the .env file exists in a parent directory."""
    parent_dir = temp_dir / "parent"
    parent_dir.mkdir()
    env_file = temp_dir / ".env"
    env_file.touch()  # Create .env in parent
    child_dir = parent_dir / "child"
    child_dir.mkdir()
    result = find_env_file(child_dir)
    assert result == env_file
    mock_logger.info.assert_called_with("Found .env file at %s", env_file)


def test_find_env_file_not_found(temp_dir: Path) -> None:
    """Test find_env_file when no .env file is found, with warning."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = find_env_file(temp_dir)
        assert result is None
        assert len(w) == 1
        assert issubclass(w[0].category, EnvFileNotFoundWarning)
        assert "No .env file found" in str(w[0].message)


def test_find_env_file_no_warning(temp_dir: Path) -> None:
    """Test find_env_file with warn_on_missing=False."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = find_env_file(temp_dir, warn_on_missing=False)
        assert result is None
        assert len(w) == 0  # No warnings issued


def test_find_env_file_invalid_start_dir(mock_path_exists: MagicMock) -> None:
    """Test find_env_file with a non-existent start directory."""
    mock_path_exists.return_value = False
    start_dir = Path("/fake/path")
    with pytest.raises(ValueError, match="Starting directory does not exist"):
        find_env_file(start_dir)


def test_find_env_file_not_directory(temp_dir: Path, mock_path_exists: MagicMock, mock_path_is_dir: MagicMock) -> None:
    """Test find_env_file when start_dir is not a directory."""
    mock_path_exists.return_value = True
    mock_path_is_dir.return_value = False
    start_dir = temp_dir / "not_a_dir"
    with pytest.raises(ValueError, match="Starting path is not a directory"):
        find_env_file(start_dir)


def test_find_env_file_invalid_filename(temp_dir: Path) -> None:
    """Test find_env_file with an invalid env_filename."""
    with pytest.raises(ValueError, match="Invalid environment filename"):
        find_env_file(temp_dir, env_filename="invalid:<name")


def test_find_env_file_custom_filename(temp_dir: Path, mock_logger: MagicMock) -> None:
    """Test find_env_file with a custom env_filename."""
    env_file = temp_dir / ".custom_env"
    env_file.touch()  # Create a custom-named file
    result = find_env_file(temp_dir, env_filename=".custom_env")
    assert result == env_file
    mock_logger.info.assert_called_with("Found .env file at %s", env_file)
