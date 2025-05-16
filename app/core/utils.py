import logging
import warnings
from pathlib import Path


logger = logging.getLogger(__name__)


class EnvFileNotFoundWarning(UserWarning):
    """Custom warning for when no .env file is found."""


def check_env_file(env_file: Path) -> bool:
    """
    Check if an environment file exists and is accessible.

    Args:
        env_file: Path to the environment file.

    Returns:
        bool: True if the file exists and is a regular file, False otherwise.

    Raises:
        PermissionError: If the file exists but cannot be accessed due to permissions.
        OSError: If other file system errors occur (e.g., path is a directory).
    """
    try:
        if env_file.is_file():
            logger.debug("Found .env file at %s", env_file)
            return True
    except PermissionError:
        logger.exception("Permission denied accessing .env file %s", env_file)
        raise
    except OSError:
        logger.exception("OS error accessing .env file %s", env_file)
        raise
    else:
        return False


def find_env_file(
    start_dir: Path,
    env_filename: str = ".env",
    *,
    warn_on_missing: bool = True,
) -> Path | None:
    """
    Search upward through parent directories for an environment file and return its path.

    Args:
        start_dir: The directory to start searching from.
        env_filename: The name of the environment file to find. Defaults to ".env".
        warn_on_missing: Whether to warn if no file is found. Defaults to True.

    Returns:
        Path | None: The path to the .env file, or None if no file was found.

    Raises:
        ValueError: If start_dir is not a directory or env_filename is invalid.
        PermissionError: If the .env file cannot be accessed due to permissions.
        OSError: If other file system errors occur during the search.

    Example:
        >>> from pathlib import Path
        >>> env_path = find_env_file(Path.cwd())
        >>> if env_path:
        ...     print(f"Found .env at {env_path}")
        ... else:
        ...     print("No .env file found")
    """
    # Validate inputs
    if not start_dir.exists():
        msg = f"Starting directory does not exist: {start_dir}"
        raise ValueError(msg)
    if not start_dir.is_dir():
        msg = f"Starting path is not a directory: {start_dir}"
        raise ValueError(msg)
    if not env_filename or any(c in env_filename for c in r'<>:"/\|?*'):
        msg = f"Invalid environment filename: {env_filename}"
        raise ValueError(msg)

    # Traverse upward until root or .env is found
    for parent in [start_dir.resolve(), *start_dir.resolve().parents]:
        env_file = parent / env_filename
        if check_env_file(env_file):
            logger.info("Found .env file at %s", env_file)
            return env_file

    # Warn if no file was found
    if warn_on_missing:
        warnings.warn(
            f"No {env_filename} file found in {start_dir} or its parent directories. "
            "Ensure a valid .env file exists or set environment variables manually.",
            EnvFileNotFoundWarning,
            stacklevel=2,
        )
    return None
