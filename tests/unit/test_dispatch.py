# tests/unit/test_dispatch.py
import pytest
from agy_orchestrator import dispatch_task, sanitize_prompt


def test_dispatch_task():
    # Test brainstorming
    assert dispatch_task("Nápad na nový projekt") == "support_mind"
    assert dispatch_task("brainstorming") == "support_mind"
    
    # Test review
    assert dispatch_task("revize kódu") == "code_revizor"
    assert dispatch_task("review") == "code_revizor"
    
    # Test code
    assert dispatch_task("napiš kód") == "coder"
    assert dispatch_task("code") == "coder"
    
    # Test fix
    assert dispatch_task("oprava chyby") == "test_fix"
    assert dispatch_task("fix bug") == "test_fix"
    
    # Test default
    assert dispatch_task("něco náhodného") == "coder"


def test_sanitize_prompt():
    # Test odstranění shellových metaznaků
    assert sanitize_prompt("ahoj; rm -rf /") == "ahoj rm -rf "
    assert sanitize_prompt("prompt | cat /etc/passwd") == "prompt  cat /etc/passwd"
    assert sanitize_prompt("normální prompt") == "normální prompt"