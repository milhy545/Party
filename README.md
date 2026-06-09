# Agy Orchestrator Squad

Multi-agent AI tým pro brainstorming, kódování, revize a opravy chyb.

## Instalace

### Rychlá instalace (doporučeno)
Použij instalační skript, který automaticky nainstaluje všechny závislosti:

```bash
curl -sSL https://raw.githubusercontent.com/milhy545/Party/main/install.sh | bash
```

Po instalaci restartuj terminál nebo spusť:
```bash
source ~/.bashrc
```

### Manuální instalace
#### Požadavky
- Python 3+
- `git`
- `tmux`
- `alacritty`
- `pi` (interaktivní AI shell)

#### Kroky
```bash
git clone https://github.com/milhy545/Party.git
cd Party
python3 -m venv .venv
source .venv/bin/activate
pip install --break-system-packages -r requirements-test.txt  # Pro testování
# Nebo ručně:
pip install --break-system-packages toml google.antigravity
```

## Použití

### Spuštění
```bash
./start_party.sh  # Nebo ./start_squad.sh (symlink)
```

### Workflow
1. **Brainstorming** (`support_mind`): Vytvoření plánu.
2. **Revize plánu** (`code_revizor`): Kontrola a schválení plánu.
3. **Kódování** (`coder`): Implementace podle schváleného plánu.
4. **Revize kódu** (`code_revizor`): Kontrola a schválení kódu.
5. **Testování/opravy** (`test_fix`): Oprava chyb.
6. **Finální revize** (`code_revizor`): Konečné schválení.
7. **Finální zhodnocení** (`support_mind`): Celkové zhodnocení.

## Konfigurace
Upravte `config.toml` pro změnu:
- **Modelů** pro jednotlivé členy týmu.
- **Timeoutů** a **maximálního počtu opakování** pro schvalovací smyčky.
- **Klíčových slov** pro automatické směrování úkolů.
- **Logování** (úroveň a cesta k log souboru).

## Řešení problémů

### Logy
Logy jsou ukládány do:
```
/tmp/agy_orchestrator_<session>.log
```

### Časté chyby
- **`tmux/pi/alacritty nenalezen`**: Nainstalujte chybějící nástroje.
- **Modely se nepřepínají**: Zkontrolujte logy a ujistěte se, že `pi` inicializuje správně.
- **Max retries reached**: Revizor opakovaně zamítá plán/kód. Zkontrolujte vstupní data.

## CI/CD

Projekt používá **GitHub Actions** pro automatizované testování a releasy:

### Workflows
- **CI**: Spouští unit a integrační testy při každém `push`/`PR` do `main`.
- **E2E Tests**: Spouští end-to-end testy při `push` do `main`.
- **Release**: Automaticky vytvoří release při vytvoření nového tagu (např. `v1.0.0`).

### Branch Protection Rules
- **`main` branch** je chráněn:
  - Vyžaduje schválení PR (min. 1 reviewer).
  - Vyžaduje úspěšné CI testy.
  - Zakazuje force push.

## Testování

### Unit testy
```bash
pytest tests/unit/
```

### Integrační testy
```bash
pytest tests/integration/
```

### E2E testy
```bash
pytest tests/e2e/
```

## Licence
MIT