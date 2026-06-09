# Agy Orchestrator Squad

Multi-agent AI tým pro brainstorming, kódování, revize a opravy chyb.

## Instalace

### Požadavky
- Python 3.12+
- `tmux`
- `alacritty`
- `pi` (interaktivní AI shell)
- `uv` (pro správu Python prostředí)

### Kroky
```bash
git clone <repo>
cd Party
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # Pokud existuje, jinak nainstaluj závislosti ručně
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