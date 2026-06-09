# tests/unit/test_logging.py
import pytest
import logging
import os
from agy_orchestrator import sanitize_prompt


def test_logging_setup():
    """Ověří, že logování je správně nastaveno."""
    log_file = "/tmp/agy_orchestrator_test.log"
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    # Zalogujeme testovací zprávu
    test_message = "Testovací zpráva"
    logging.info(test_message)
    
    # Ověříme, že log soubor existuje a obsahuje zprávu
    assert os.path.exists(log_file)
    with open(log_file, "r") as f:
        logs = f.read()
        assert test_message in logs
    
    # Vyčistíme
    os.remove(log_file)


def test_sanitize_prompt_logging(caplog):
    """Ověří, že sanitizace vstupu je zalogována."""
    test_prompt = "test; rm -rf /"
    sanitized = sanitize_prompt(test_prompt)
    
    # Ověříme, že sanitizace byla zalogována
    assert "Úkol odeslán" in caplog.text
    assert sanitized in caplog.text