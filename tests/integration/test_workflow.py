# tests/integration/test_workflow.py
import pytest
import subprocess
import time
import os
from agy_orchestrator import send_to_squad, read_from_squad


@pytest.fixture(scope="module")
def tmux_session():
    # Spustí tmux session pro testování
    session_name = "test_squad"
    subprocess.run(["tmux", "new-session", "-d", "-s", session_name, "pi"])
    time.sleep(2)  # Počkáme na inicializaci pi
    yield session_name
    subprocess.run(["tmux", "kill-session", "-t", session_name])


def test_send_and_read(tmux_session):
    # Otestuje odeslání a přijetí zprávy
    test_prompt = "Testovací zpráva"
    response = send_to_squad("support_mind", test_prompt)
    assert "Úkol úspěšně odeslán" in response
    
    # Počkáme na zpracování
    time.sleep(1)
    
    # Přečteme odpověď
    output = read_from_squad("support_mind")
    assert "Testovací zpráva" in output
    assert "Chyba" not in output