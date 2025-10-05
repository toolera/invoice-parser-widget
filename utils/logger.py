"""Logging utilities for invoice parser widget."""

import logging
import sys
from pathlib import Path
from typing import Optional


class InvoiceLogger:
    """Custom logger for invoice parser operations."""

    def __init__(self, name: str = "invoice_parser", log_file: Optional[str] = None):
        """
        Initialize logger.

        Args:
            name: Logger name
            log_file: Optional log file path
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Avoid duplicate handlers
        if not self.logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

            # File handler (if specified)
            if log_file:
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(logging.DEBUG)
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                file_handler.setFormatter(file_formatter)
                self.logger.addHandler(file_handler)

    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)

    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)

    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)

    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)

    def step(self, step_num: int, total_steps: int, message: str):
        """Log a processing step."""
        self.logger.info(f"[Step {step_num}/{total_steps}] {message}")


def setup_logger(log_dir: Optional[Path] = None) -> InvoiceLogger:
    """
    Setup logger with optional file output.

    Args:
        log_dir: Directory for log files

    Returns:
        Configured InvoiceLogger instance
    """
    log_file = None
    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "invoice_parser.log"

    return InvoiceLogger(log_file=str(log_file) if log_file else None)
