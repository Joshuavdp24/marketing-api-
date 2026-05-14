import os
import importlib
import pytest


def test_settings_loads_required_vars(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setenv("VALID_API_KEYS", "mk_live_abc,mk_live_xyz")

    import config
    config.get_settings.cache_clear()
    importlib.reload(config)
    config.get_settings.cache_clear()

    settings = config.get_settings()
    assert settings.anthropic_api_key == "test-anthropic-key"


def test_get_api_keys_returns_set(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("VALID_API_KEYS", "mk_live_abc,mk_live_xyz")

    import config
    config.get_settings.cache_clear()
    importlib.reload(config)
    config.get_settings.cache_clear()

    keys = config.get_settings().get_api_keys()
    assert "mk_live_abc" in keys
    assert "mk_live_xyz" in keys
    assert len(keys) == 2


def test_get_api_keys_strips_whitespace(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("VALID_API_KEYS", "mk_live_abc, mk_live_xyz")

    import config
    config.get_settings.cache_clear()
    importlib.reload(config)
    config.get_settings.cache_clear()

    keys = config.get_settings().get_api_keys()
    assert "mk_live_abc" in keys
    assert "mk_live_xyz" in keys


def test_model_default(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("VALID_API_KEYS", "mk_live_abc")

    import config
    config.get_settings.cache_clear()
    importlib.reload(config)
    config.get_settings.cache_clear()

    assert config.get_settings().model == "claude-sonnet-4-6"
