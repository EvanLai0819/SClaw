"""Structured logging for SClaw."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Optional

# Global verbose flag - also check env var at startup
_verbose = os.environ.get("SCLAW_VERBOSE", "").lower() in ("1", "true", "yes")


def set_verbose(verbose: bool) -> None:
    """Enable or disable verbose (DEBUG) logging for all sclaw loggers."""
    global _verbose
    _verbose = verbose
    level = logging.DEBUG if verbose else logging.INFO

    # Update root sclaw logger and its handlers
    root = logging.getLogger("sclaw")
    root.setLevel(level)
    for handler in root.handlers:
        handler.setLevel(level)

    # Also update root logger if no handlers on sclaw
    if not root.handlers:
        # Ensure sclaw logger has a handler
        setup_logger("sclaw", level)

    # Update all existing child loggers
    for name in list(logging.Logger.manager.loggerDict.keys()):
        if name.startswith("sclaw"):
            child = logging.getLogger(name)
            child.setLevel(level)
            for handler in child.handlers:
                handler.setLevel(level)


def setup_logger(
    name: str = "sclaw",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    log_config: Optional[dict] = None,
) -> logging.Logger:
    """
    Set up a logger with console and optional file output.

    Args:
        name: Logger name
        level: Logging level
        log_file: Optional file path for logging
        log_config: Optional logging configuration dict with 'level' and 'file' keys

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Use verbose level if set globally
    if _verbose:
        level = logging.DEBUG
    
    # Override level from config if provided
    if log_config:
        if log_config.get("level"):
            level_str = log_config["level"].upper()
            if level_str == "DEBUG":
                level = logging.DEBUG
            elif level_str == "INFO":
                level = logging.INFO
            elif level_str == "WARNING":
                level = logging.WARNING
            elif level_str == "ERROR":
                level = logging.ERROR
        
        if log_config.get("file"):
            log_file = log_config["file"]

    logger.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Format: timestamp - level - message
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    
    # Add console handler if not already present
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        # Check if file handler already exists
        if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
            # Convert to absolute path and ensure directory exists
            log_path = Path(log_file).expanduser()  # Expand ~ to home directory
            if not log_path.is_absolute():
                # Use current working directory if relative path
                log_path = Path.cwd() / log_file
            
            # Create parent directory if it doesn't exist
            try:
                log_path.parent.mkdir(parents=True, exist_ok=True)
            except (IOError, OSError) as e:
                print(f"Warning: Failed to create log directory {log_path.parent}: {e}", file=sys.stderr)
                return logger
            
            try:
                file_handler = logging.FileHandler(str(log_path))
                file_handler.setLevel(level)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except (IOError, OSError) as e:
                # If file creation fails, log to console and continue
                print(f"Warning: Failed to create log file at {log_path}: {e}", file=sys.stderr)

    return logger


# Global logger instance
logger = setup_logger()


def get_logger(name: str = "sclaw") -> logging.Logger:
    """Get a logger instance."""
    child = logging.getLogger(name)
    # Apply verbose level if set globally
    if _verbose:
        child.setLevel(logging.DEBUG)
    return child
