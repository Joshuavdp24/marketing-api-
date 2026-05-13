import os
import pytest

def test_settings_loads_required_vars(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setenv("VALID_API_KEYS", "mk_live_abc,mk_live_xyz")

    import importlib
    import config
    importlib.reload(config)

    assert config.settings.anthropic_api_key == "test-anthropic-key"

def test_get_api_keys_returns_set(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("VALID_API_KEYS", "mk_live_abc,mk_live_xyz")

    import importlib
    import config
    importlib.reload(config)

    keys = config.settings.get_api_keys()
    assert "mk_live_abc" in keys
    assert "mk_live_xyz" in keys
    assert len(keys) == 2


import pytest
