import os
import subprocess
import asyncio
import re
import logging
import toml
from typing import Literal, Dict, List
from google.antigravity import Agent, LocalAgentConfig
from google.antigravity.types import TemplatedSystemInstructions

# Načtení konfigurace
config = toml.load("/home/milhy777/Develop/Party/config.toml")

# Nastavení logování
logging.basicConfig(
    filename=config["logging"]["log_file"].format(session=os.path.basename(os.getcwd())),
    level=getattr(logging, config["logging"]["log_level"].upper()),
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Dispatch rules: map keywords to squad members
DISPATCH_RULES: Dict[str, List[str]] = {
    member: keywords for member, keywords in config["dispatch_rules"].items()
}

# Konstanty z konfigurace
MAX_RETRIES = config["workflow"]["max_retries"]
TIMEOUT_SECONDS = config["workflow"]["timeout_seconds"]
SKIP_STEPS = config["workflow"]["skip_steps"]


def sanitize_prompt(prompt: str) -> str:
    """Odstraní shellové metaznaky z promptu."""
    return re.sub(r"[;\n\r|&<>]", "", prompt)

def dispatch_task(prompt: str) -> str:
    """Determine which squad member should handle the prompt.
    Simple keyword matching based on DISPATCH_RULES. Returns the member name.
    """
    lowered = prompt.lower()
    for keyword, member in DISPATCH_RULES.items():
        if keyword in lowered:
            return member
    # Default to coder if no keyword matches
    return "coder"


# Automatické zjištění jména projektu ze složky, kde to spouštíš
PROJECT_NAME = os.path.basename(os.getcwd())
SESSION_NAME = f"squad_{PROJECT_NAME}"

# --- Nástroje (Zbraně) pro Agyho ---

PANE_MAP = {
    "support_mind": "0", # vlevo nahoře
    "code_revizor": "1", # vlevo dole
    "coder": "2",        # vpravo nahoře
    "test_fix": "3"      # vpravo dole
}

def send_to_squad(member: Literal["support_mind", "code_revizor", "coder", "test_fix"], prompt: str) -> str:
    """
    Odešle zprávu/prompt konkrétnímu členovi týmu v jeho tmux panelu a počká na potvrzení.
    Sanitizuje vstup proti command injection.
    """
    sanitized_prompt = sanitize_prompt(prompt)
    pane_idx = PANE_MAP[member]
    target = f"{SESSION_NAME}:0.{pane_idx}"
    
    # Zapíšeme prompt do dočasného souboru (jméno souboru je unikátní pro projekt)
    tmp_file = f"/tmp/agy_prompt_{SESSION_NAME}_{member}.txt"
    with open(tmp_file, "w", encoding="utf-8") as f:
        f.write(sanitized_prompt + "\n")
        
    with open(tmp_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    subprocess.run(["tmux", "set-buffer", content])
    subprocess.run(["tmux", "paste-buffer", "-t", target])
    subprocess.run(["tmux", "send-keys", "-t", target, "Enter"])
    
    logging.info(f"Úkol odeslán do {member}: {sanitized_prompt}")
    return f"Úkol úspěšně odeslán do panelu {target} ({member})."

def read_from_squad(member: Literal["support_mind", "code_revizor", "coder", "test_fix"], lines: int = 40) -> str:
    """
    Přečte posledních X řádků z tmux panelu konkrétního člena.
    """
    pane_idx = PANE_MAP[member]
    target = f"{SESSION_NAME}:0.{pane_idx}"
    result = subprocess.run(
        ["tmux", "capture-pane", "-p", "-t", target, "-S", f"-{lines}"], 
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return f"Chyba při čtení tmux panelu: {result.stderr}"
    
    return result.stdout.strip()


async def main():
    print(f"Spouštím Agy Orchestratora pro projekt: '{PROJECT_NAME}'")
    
    agy_config = LocalAgentConfig(
        model="opencode/mimo-v2.5-free",
        system_instructions=TemplatedSystemInstructions(
            identity=(
                f"Jsi 'Agy', Hlavní orchestrátor pro projekt '{PROJECT_NAME}'. Jsi aktivní myslitel.\n\n"
                f"Máš k dispozici tým '{SESSION_NAME}', který běží ve 4 tmux panelech:\n"
                "1. 'support_mind' (mimo) -> Tvůj brainstorming parťák. Můžete se pohádat o plán, dokud nevymyslíte to nejlepší.\n"
                "2. 'code_revizor' (mistral) -> Nekompromisní fackovač. Hledá chyby v plánu i v kódu. NIC neprojde dál bez jeho [REVIZE: SCHVÁLENO]. Má čistý kontext.\n"
                "3. 'coder' (codestral/nemotron) -> Dělá těžkou dřinu. Píše veškerý kód podle schváleného plánu.\n"
                "4. 'test_fix' (deepseek) -> Dělá super-rychlé fixy na základě pádů a chybových výpisů z terminálu.\n\n"
                "TVOJE ZBRANĚ (Nástroje):\n"
                "- send_to_squad(member, prompt): pro posílání úkolů.\n"
                "- read_from_squad(member, lines): abys viděl odpovědi.\n\n"
                "Očekávej úkol od Milhyho."
            )
        ),
        tools=[send_to_squad, read_from_squad]
    )

    async with Agent(agy_config) as agy:
        print(f"\n[AGY] Připojen k tmux session '{SESSION_NAME}'. Očekávám úkol.")
        
        while True:
            try:
                user_input = input("\nMilhy: ")
                if user_input.strip() == "":
                    continue
                if user_input.lower() in ["exit", "quit"]:
                    break

                # Initial prompt from user is the high‑level task/idea
                current_prompt = user_input.strip()
                # Step 1 – brainstorming with support_mind
                print("[AGY] 🔎 Odesílám úkol do support_mind (brainstorming)…")
                send_to_squad("support_mind", current_prompt)
                brainstorming = read_from_squad("support_mind")
                print(f"\n[SUPPORT_MIND response]:\n{brainstorming}\n")

                # Prepare plan (use brainstorming as basis)
                plan = brainstorming
                # Step 2 – review by code_revizor
                retry_count = 0
                while retry_count < MAX_RETRIES:
                    print(f"[AGY] 📋 Posílám plán do code_revizor (revize) – pokus {retry_count + 1}/{MAX_RETRIES}…")
                    send_to_squad("code_revizor", plan)
                    revizor_output = read_from_squad("code_revizor")
                    print(f"\n[CODE_REVIZOR response]:\n{revizor_output}\n")
                    if "SCHVÁLENO" in revizor_output.upper() or "APPROVED" in revizor_output.upper():
                        print("[AGY] ✅ Revizor schválil plán.")
                        break
                    else:
                        retry_count += 1
                        if retry_count >= MAX_RETRIES:
                            print(f"[AGY] ❌ Revizor plán zamítl {MAX_RETRIES}x. Ukončuji workflow.")
                            logging.error("Max retries reached for plan review")
                            break
                        # Send back to support_mind for re‑brainstorming
                        print("[AGY] ⚠️ Revizor požaduje úpravu – posílám zpět do support_mind…")
                        send_to_squad("support_mind", revizor_output)
                        plan = read_from_squad("support_mind")
                        print(f"\n[SUPPORT_MIND updated]:\n{plan}\n")

                # Step 3 – coding by coder
                print("[AGY] 🛠️ Zadávám kódování do coder…")
                send_to_squad("coder", plan)
                code_output = read_from_squad("coder")
                print(f"\n[CODER response]:\n{code_output}\n")

                # Step 4 – review by code_revizor before testing
                retry_count = 0
                while retry_count < MAX_RETRIES:
                    print(f"[AGY] 📋 Posílám kód do code_revizor (revize) – pokus {retry_count + 1}/{MAX_RETRIES}…")
                    send_to_squad("code_revizor", code_output)
                    rev_output = read_from_squad("code_revizor")
                    print(f"\n[CODE_REVIZOR response]:\n{rev_output}\n")
                    if "SCHVÁLENO" in rev_output.upper() or "APPROVED" in rev_output.upper():
                        print("[AGY] ✅ Revizor schválil kód.")
                        break
                    else:
                        retry_count += 1
                        if retry_count >= MAX_RETRIES:
                            print(f"[AGY] ❌ Revizor kód zamítl {MAX_RETRIES}x. Ukončuji workflow.")
                            logging.error("Max retries reached for code review")
                            break
                        print("[AGY] ⚠️ Revizor požaduje úpravy – posílám zpět do coder…")
                        send_to_squad("coder", rev_output)
                        code_output = read_from_squad("coder")
                        print(f"\n[CODER re‑adjusted]:\n{code_output}\n")

                # Step 5 – testing/fixing by test_fix
                print("[AGY] 🧪 Spouštím test_fix na výstup z coder…")
                send_to_squad("test_fix", code_output)
                fix_output = read_from_squad("test_fix")
                print(f"\n[TEST_FIX response]:\n{fix_output}\n")

                # Step 5 – final review by code_revizor
                retry_count = 0
                while retry_count < MAX_RETRIES:
                    print(f"[AGY] 📋 Posílám finální výstup do code_revizor (konečná revize) – pokus {retry_count + 1}/{MAX_RETRIES}…")
                    send_to_squad("code_revizor", fix_output)
                    final_rev = read_from_squad("code_revizor")
                    print(f"\n[CODE_REVIZOR final response]:\n{final_rev}\n")
                    if "SCHVÁLENO" in final_rev.upper() or "APPROVED" in final_rev.upper():
                        print("[AGY] ✅ Konečná revize schválena.")
                        break
                    else:
                        retry_count += 1
                        if retry_count >= MAX_RETRIES:
                            print(f"[AGY] ❌ Konečná revize zamítnuta {MAX_RETRIES}x. Ukončuji workflow.")
                            logging.error("Max retries reached for final review")
                            break
                        # If not approved, send back to coder for adjustments
                        print("[AGY] ⚠️ Konečná revize požaduje úpravy – posílám zpět do coder…")
                        send_to_squad("coder", final_rev)
                        fix_output = read_from_squad("coder")
                        print(f"\n[CODER re‑adjusted]:\n{fix_output}\n")

                # Step 6 – final assessment by support_mind
                print("[AGY] 🔍 Posílám finální produkt do support_mind pro celistvé zhodnocení…")
                send_to_squad("support_mind", fix_output)
                final_assessment = read_from_squad("support_mind")
                print(f"\n[SUPPORT_MIND final assessment]:\n{final_assessment}\n")
                print("[AGY] 🎉 Workflow dokončen. Čekám na další úkol.")
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    asyncio.run(main())
