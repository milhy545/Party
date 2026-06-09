# tests/unit/test_config.py
import pytest
import toml
from pathlib import Path


def test_config_validity():
    """Ověří, že config.toml je validní a obsahuje všechny požadované klíče."""
    config_path = Path("/home/milhy777/Develop/Party/config.toml")
    config = toml.load(config_path)
    
    # Ověření sekcí
    assert "models" in config
    assert "workflow" in config
    assert "logging" in config
    assert "dispatch_rules" in config
    
    # Ověření modelů
    models = config["models"]
    assert "support_mind" in models
    assert "code_revizor" in models
    assert "coder" in models
    assert "test_fix" in models
    
    # Ověření workflow
    workflow = config["workflow"]
    assert "max_retries" in workflow
    assert "timeout_seconds" in workflow
    assert "skip_steps" in workflow
    
    # Ověření logování
    logging = config["logging"]
    assert "log_file" in logging
    assert "log_level" in logging