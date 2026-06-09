#!/usr/bin/env bash
# install.sh – Instalační skript pro Agy Orchestrator Squad

set -uo pipefail

DRY_RUN=false
if [[ "$*" == *--dry-run* ]]; then
    DRY_RUN=true
    echo -e "\033[1;33m🧪 Spuštěn testovací režim (--dry-run). Žádné změny nebudou provedeny.\033[0m"
fi

# Barvy pro výstup
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Cesta k repozitáři
REPO_DIR="$HOME/Develop/Party"
VENV_DIR="$REPO_DIR/.venv"

# Funkce pro kontrolu a instalaci nástrojů
install_system_deps() {
    echo -e "${YELLOW}🔍 Kontroluji systémové nástroje...${NC}"

    # Kontrola a instalace git
    if ! command -v git &> /dev/null; then
        echo -e "${RED}❌ git není nainstalován.${NC}"
        if [ "$DRY_RUN" = false ]; then
            echo -e "${YELLOW}🔧 Instaluji git...${NC}"
            sudo apt-get update && sudo apt-get install -y git
        else
            echo -e "${YELLOW}🔧 [DRY RUN] Instalace git...${NC}"
        fi
    else
        echo -e "${GREEN}✅ git je nainstalován.${NC}"
    fi

    # Kontrola a instalace tmux
    if ! command -v tmux &> /dev/null; then
        echo -e "${RED}❌ tmux není nainstalován.${NC}"
        if [ "$DRY_RUN" = false ]; then
            echo -e "${YELLOW}🔧 Instaluji tmux...${NC}"
            sudo apt-get install -y tmux
        else
            echo -e "${YELLOW}🔧 [DRY RUN] Instalace tmux...${NC}"
        fi
    else
        echo -e "${GREEN}✅ tmux je nainstalován.${NC}"
    fi

    # Kontrola a instalace alacritty
    if ! command -v alacritty &> /dev/null; then
        echo -e "${RED}❌ alacritty není nainstalován.${NC}"
        if [ "$DRY_RUN" = false ]; then
            echo -e "${YELLOW}🔧 Instaluji alacritty...${NC}"
            sudo apt-get install -y alacritty
        else
            echo -e "${YELLOW}🔧 [DRY RUN] Instalace alacritty...${NC}"
        fi
    else
        echo -e "${GREEN}✅ alacritty je nainstalován.${NC}"
    fi

    # Kontrola Python 3+
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3+ není nainstalován.${NC}"
        if [ "$DRY_RUN" = false ]; then
            echo -e "${YELLOW}🔧 Instaluji Python 3...${NC}"
            sudo apt-get install -y python3 python3-venv python3-dev
        else
            echo -e "${YELLOW}🔧 [DRY RUN] Instalace Python 3...${NC}"
        fi
    else
        echo -e "${GREEN}✅ Python 3+ je nainstalován.${NC}"
    fi
}

# Klonování repozitáře
clone_repo() {
    if [ ! -d "$REPO_DIR" ]; then
        echo -e "${YELLOW}📥 Klonuji repozitář...${NC}"
        if [ "$DRY_RUN" = false ]; then
            mkdir -p "$(dirname "$REPO_DIR")"
            git clone https://github.com/milhy545/Party.git "$REPO_DIR"
        else
            echo -e "${YELLOW}🔧 [DRY RUN] Klonování repozitáře...${NC}"
        fi
    else
        echo -e "${GREEN}✅ Repozitář již existuje.${NC}"
        echo -e "${YELLOW}🔄 Aktualizuji repozitář...${NC}"
        if [ "$DRY_RUN" = false ]; then
            cd "$REPO_DIR" && git pull
        else
            echo -e "${YELLOW}🔧 [DRY RUN] Aktualizace repozitáře...${NC}"
        fi
    fi
}

# Vytvoření virtuálního prostředí a instalace závislostí
setup_venv() {
    echo -e "${YELLOW}🐍 Vytvářím virtuální prostředí...${NC}"
    if [ "$DRY_RUN" = false ]; then
        cd "$REPO_DIR"
        python3 -m venv "$VENV_DIR"
        source "$VENV_DIR/bin/activate"
        pip install --upgrade pip
        pip install --break-system-packages -r requirements-test.txt
    else
        echo -e "${YELLOW}🔧 [DRY RUN] Vytvoření virtuálního prostředí a instalace závislostí...${NC}"
    fi
}

# Instalace pi (interaktivní AI shell)
install_pi() {
    echo -e "${YELLOW}🤖 Instaluji pi (interaktivní AI shell)...${NC}"
    if ! command -v pi &> /dev/null; then
        if [ "$DRY_RUN" = false ]; then
            # Stažení a instalace pi (příklad pro Linux)
            curl -sSL https://raw.githubusercontent.com/ekzhang/pi/main/install.sh | bash
            # Přidání do PATH (pokud není)
            if [ -d "$HOME/.local/bin" ] && ! grep -q "$HOME/.local/bin" "$HOME/.bashrc"; then
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
                source "$HOME/.bashrc"
            fi
        else
            echo -e "${YELLOW}🔧 [DRY RUN] Instalace pi...${NC}"
        fi
    else
        echo -e "${GREEN}✅ pi již je nainstalován.${NC}"
    fi
}

# Nastavení config.toml
setup_config() {
    echo -e "${YELLOW}⚙️ Nastavuji config.toml...${NC}"
    if [ ! -f "$REPO_DIR/config.toml" ]; then
        if [ "$DRY_RUN" = false ]; then
            cat > "$REPO_DIR/config.toml" <<EOL
[models]
support_mind = "opencode/mimo-v2.5-free"
code_revizor = "mistral/mistral-large-latest"
coder = "mistral/codestral-latest"
test_fix = "opencode/deepseek-v4-flash-free"

[workflow]
max_retries = 5
timeout_seconds = 30
skip_steps = []

[logging]
log_file = "/tmp/agy_orchestrator_{session}.log"
log_level = "INFO"

[dispatch_rules]
brainstorm = ["brainstorm", "idea", "plán"]
review = ["review", "revize", "kontrola"]
code = ["code", "write", "kód"]
fix = ["fix", "bug", "error", "oprava"]
EOL
        else
            echo -e "${YELLOW}🔧 [DRY RUN] Vytvoření config.toml...${NC}"
        fi
    else
        echo -e "${GREEN}✅ config.toml již existuje.${NC}"
    fi
}

# Vytvoření aliasů
setup_aliases() {
    echo -e "${YELLOW}🔗 Vytvářím aliasy...${NC}"
    if [ "$DRY_RUN" = false ]; then
        # Alias pro start_party.sh
        if ! grep -q "alias party=" "$HOME/.bashrc"; then
            echo "alias party='$REPO_DIR/start_party.sh'" >> "$HOME/.bashrc"
        fi
        # Alias pro start_squad.sh
        if ! grep -q "alias squad=" "$HOME/.bashrc"; then
            echo "alias squad='$REPO_DIR/start_squad.sh'" >> "$HOME/.bashrc"
        fi
        source "$HOME/.bashrc"
    else
        echo -e "${YELLOW}🔧 [DRY RUN] Vytvoření aliasů...${NC}"
    fi
}

# Hlavní funkce
main() {
    echo -e "${GREEN}🚀 Instalace Agy Orchestrator Squad${NC}"
    install_system_deps
    clone_repo
    setup_venv
    install_pi
    setup_config
    setup_aliases
    echo -e "${GREEN}✅ Instalace dokončena!${NC}"
    echo -e "${YELLOW}📌 Pro spuštění použij:${NC}"
    echo -e "  ${GREEN}party${NC} nebo ${GREEN}squad${NC}"
}

main