#!/usr/bin/env bash
# start_party.sh – spustí tmux session s čtyřmi panely pro aktuální projekt v Alacritty
# a v aktuálním okně spustí Agy Orchestratora.

PROJECT_NAME=$(basename "$PWD")
SESSION_NAME="squad_${PROJECT_NAME}"
SCRIPT_DIR="/home/milhy777/Develop/Party"

# Najdeme binárku Alacritty
ALACRITTY_BIN=$(which alacritty 2>/dev/null || echo "/snap/bin/alacritty")

if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
  echo "Vytvářím novou tmux session '$SESSION_NAME' pro projekt '$PROJECT_NAME'..."
  
  # Krok 1: Inicializace session a nastavení base-indexů
  tmux new-session -d -s "$SESSION_NAME" -n "temp"
  tmux set-option -t "$SESSION_NAME" base-index 0
  
  # Vytvoření hlavního okna "0" se spuštěným "pi"
  tmux new-window -t "${SESSION_NAME}:0" -n "0" "pi"
  tmux kill-window -t "${SESSION_NAME}:temp"
  
  # Nastavení pane-base-index 0 pro okno 0 (pro shodu s agy_orchestrator.py)
  tmux set-window-option -t "${SESSION_NAME}:0" pane-base-index 0
  
  # Krok 2: Rozdělení do 2x2 gridu (tiled layout)
  tmux split-window -t "${SESSION_NAME}:0" -h -p 50 "pi"
  tmux split-window -t "${SESSION_NAME}:0.0" -v -p 50 "pi"
  tmux split-window -t "${SESSION_NAME}:0.2" -v -p 50 "pi"
  tmux select-layout -t "${SESSION_NAME}:0" tiled
  
  # Krok 3: Pre-flight kontroly
  command -v tmux >/dev/null || { echo "Chyba: tmux není nainstalován"; exit 1; }
  command -v pi >/dev/null || { echo "Chyba: pi není nainstalován"; exit 1; }
  command -v alacritty >/dev/null || { echo "Chyba: alacritty není nainstalován"; exit 1; }

  # Krok 4: Čekání na inicializaci všech čtyř 'pi' instancí
  echo "Čekám na inicializaci 'pi' instancí..."
  for idx in 0 1 2 3; do
    pane_target="${SESSION_NAME}:0.${idx}"
    for i in {1..20}; do
      if tmux capture-pane -p -t "$pane_target" | grep -q "Model set"; then
        break
      fi
      sleep 0.5
    done
  done
  
  # Krok 4: Načtení modelů do jednotlivých panelů
  declare -A PANEL_MODEL=(
    [0]="opencode/mimo-v2.5-free"         # support_mind
    [1]="mistral/mistral-large-latest"    # code_revizor
    [2]="mistral/codestral-latest"         # coder
    [3]="opencode/deepseek-v4-flash-free"  # test_fix
  )
  
  echo "Nastavuji modely v panelech..."
  for idx in 0 1 2 3; do
    pane_target="${SESSION_NAME}:0.${idx}"
    model=${PANEL_MODEL[$idx]}
    tmux send-keys -t "$pane_target" "/model" C-m
    sleep 0.5
    tmux send-keys -t "$pane_target" "$model" C-m
    sleep 0.5
    tmux send-keys -t "$pane_target" "Enter" C-m
    sleep 0.3
  done
  echo "Session '$SESSION_NAME' byla úspěšně vytvořena a inicializována."
else
  echo "Tmux session '$SESSION_NAME' již běží."
fi

# Krok 5: Spuštění tmux session v samostatném okně Alacritty
echo "Připojuji tmux session v novém Alacritty okně..."
"$ALACRITTY_BIN" -e tmux attach -t "$SESSION_NAME" &

# Krok 6: Spuštění Agy Orchestratora v aktuálním terminálu
echo "Spouštím Agy Orchestrator..."
GEMINI_API_KEY=dummy "$SCRIPT_DIR/.venv/bin/python" "$SCRIPT_DIR/agy_orchestrator.py"

