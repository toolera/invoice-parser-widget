"""Configuration management for invoice parser widget."""

import os
from typing import Optional


class Config:
    """Configuration handler for the invoice parser."""

    # AI Provider settings
    DEFAULT_AI_PROVIDER = 'openai'
    SUPPORTED_AI_PROVIDERS = ['openai', 'anthropic']

    # Model configurations
    OPENAI_MODELS = {
        'gpt-4': 'gpt-4',
        'gpt-4-turbo': 'gpt-4-turbo-preview',
        'gpt-3.5-turbo': 'gpt-3.5-turbo',
    }

    ANTHROPIC_MODELS = {
        'claude-3-5-sonnet': 'claude-3-5-sonnet-20241022',
        'claude-3-opus': 'claude-3-opus-20240229',
        'claude-3-sonnet': 'claude-3-sonnet-20240229',
    }

    # Output formats
    SUPPORTED_OUTPUT_FORMATS = ['csv', 'json', 'both']
    DEFAULT_OUTPUT_FORMAT = 'csv'

    # File settings
    MAX_FILE_SIZE_MB = 5
    SUPPORTED_FILE_TYPES = ['.pdf']

    # Memory limits
    MAX_MEMORY_MB = 512

    @staticmethod
    def get_api_key(provider: str) -> Optional[str]:
        """Get API key for specified provider."""
        if provider.lower() == 'openai':
            return os.environ.get('OPENAI_API_KEY')
        elif provider.lower() == 'anthropic':
            return os.environ.get('ANTHROPIC_API_KEY')
        return None

    @staticmethod
    def validate_provider(provider: str) -> str:
        """Validate and return normalized provider name."""
        provider = provider.lower() if provider else Config.DEFAULT_AI_PROVIDER
        if provider not in Config.SUPPORTED_AI_PROVIDERS:
            raise ValueError(
                f"Unsupported AI provider: {provider}. "
                f"Supported providers: {', '.join(Config.SUPPORTED_AI_PROVIDERS)}"
            )
        return provider

    @staticmethod
    def validate_output_format(output_format: str) -> str:
        """Validate and return normalized output format."""
        output_format = output_format.lower() if output_format else Config.DEFAULT_OUTPUT_FORMAT
        if output_format not in Config.SUPPORTED_OUTPUT_FORMATS:
            raise ValueError(
                f"Unsupported output format: {output_format}. "
                f"Supported formats: {', '.join(Config.SUPPORTED_OUTPUT_FORMATS)}"
            )
        return output_format

    @staticmethod
    def get_model_name(provider: str, model_key: str = None) -> str:
        """Get the actual model name for the provider."""
        provider = provider.lower()

        if provider == 'openai':
            return Config.OPENAI_MODELS.get(model_key, 'gpt-4')
        elif provider == 'anthropic':
            return Config.ANTHROPIC_MODELS.get(model_key, 'claude-3-5-sonnet-20241022')

        return 'gpt-4'  # Fallback
