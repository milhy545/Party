# tests/e2e/test_e2e.py
import pytest
import subprocess
import time
import os
import signal


@pytest.fixture(scope="module")
def start_orchestrator():
    # Spustí orchestrátor v samostatném procesu
    process = subprocess.Popen(
        ["python", "agy_orchestrator.py"],
        cwd="/home/milhy777/Develop/Party",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    time.sleep(5)  # Počkáme na inicializaci
    yield process
    process.send_signal(signal.SIGINT)
    process.wait()


def test_orchestrator_workflow(start_orchestrator):
    # Otestuje celý workflow
    process = start_orchestrator
    
    # Odešleme testovací úkol
    process.stdin.write("Napiš jednoduchý Python skript, který vypíše 'Ahoj světe'\n")
    process.stdin.flush()
    
    # Počkáme na zpracování (timeout 60s)
    timeout = 60
    start_time = time.time()
    output = ""
    
    while time.time() - start_time < timeout:
        line = process.stdout.readline()
        if not line:
            break
        output += line
        if "Workflow dokončen" in line:
            break
        time.sleep(0.1)
    
    # Zkontrolujeme výstup
    assert "Workflow dokončen" in output
    assert "❌" not in output  # Žádné chyby