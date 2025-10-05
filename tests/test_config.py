"""Tests for config module."""

import pytest
import os
from utils.config import Config


def test_validate_provider_openai():
    """Test OpenAI provider validation."""
    assert Config.validate_provider('openai') == 'openai'
    assert Config.validate_provider('OpenAI') == 'openai'
    assert Config.validate_provider('OPENAI') == 'openai'


def test_validate_provider_anthropic():
    """Test Anthropic provider validation."""
    assert Config.validate_provider('anthropic') == 'anthropic'
    assert Config.validate_provider('Anthropic') == 'anthropic'


def test_validate_provider_invalid():
    """Test invalid provider raises error."""
    with pytest.raises(ValueError, match="Unsupported AI provider"):
        Config.validate_provider('invalid')


def test_validate_provider_none():
    """Test None provider uses default."""
    assert Config.validate_provider(None) == 'openai'


def test_validate_output_format_csv():
    """Test CSV format validation."""
    assert Config.validate_output_format('csv') == 'csv'
    assert Config.validate_output_format('CSV') == 'csv'


def test_validate_output_format_json():
    """Test JSON format validation."""
    assert Config.validate_output_format('json') == 'json'
    assert Config.validate_output_format('JSON') == 'json'


def test_validate_output_format_both():
    """Test both format validation."""
    assert Config.validate_output_format('both') == 'both'


def test_validate_output_format_invalid():
    """Test invalid format raises error."""
    with pytest.raises(ValueError, match="Unsupported output format"):
        Config.validate_output_format('xml')


def test_validate_output_format_none():
    """Test None format uses default."""
    assert Config.validate_output_format(None) == 'csv'


def test_get_api_key_openai():
    """Test getting OpenAI API key."""
    os.environ['OPENAI_API_KEY'] = 'test-key'
    assert Config.get_api_key('openai') == 'test-key'
    del os.environ['OPENAI_API_KEY']


def test_get_api_key_anthropic():
    """Test getting Anthropic API key."""
    os.environ['ANTHROPIC_API_KEY'] = 'test-key'
    assert Config.get_api_key('anthropic') == 'test-key'
    del os.environ['ANTHROPIC_API_KEY']


def test_get_api_key_not_set():
    """Test getting API key when not set."""
    # Make sure key is not set
    if 'TEST_KEY' in os.environ:
        del os.environ['TEST_KEY']

    assert Config.get_api_key('openai') is None


def test_get_model_name_openai():
    """Test getting OpenAI model name."""
    assert Config.get_model_name('openai', 'gpt-4') == 'gpt-4'


def test_get_model_name_anthropic():
    """Test getting Anthropic model name."""
    model = Config.get_model_name('anthropic', 'claude-3-5-sonnet')
    assert 'claude-3-5-sonnet' in model


def test_supported_providers():
    """Test supported providers list."""
    assert 'openai' in Config.SUPPORTED_AI_PROVIDERS
    assert 'anthropic' in Config.SUPPORTED_AI_PROVIDERS


def test_supported_formats():
    """Test supported formats list."""
    assert 'csv' in Config.SUPPORTED_OUTPUT_FORMATS
    assert 'json' in Config.SUPPORTED_OUTPUT_FORMATS
    assert 'both' in Config.SUPPORTED_OUTPUT_FORMATS
