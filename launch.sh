#!/usr/bin/env bash
# launch.sh – Start the Enterprise RAG platform
#
# Usage:  bash launch.sh
#
# What it does:
#   1. Checks Docker Desktop is fully running
#   2. Removes the stale socket if present
#   3. Sets the correct Docker context
#   4. Runs docker compose up --build

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOCKET="/Users/$USER/.docker/run/docker.sock"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   Enterprise RAG Platform — Launcher     ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── 1. Check Docker socket is alive ───────────────────────────────────────
echo "▶  Checking Docker daemon..."

if ! nc -z -U "$SOCKET" 2>/dev/null; then
  echo ""
  echo "  ❌  Docker daemon is NOT running."
  echo ""
  echo "  Please:"
  echo "    1. Open Docker Desktop from Applications"
  echo "    2. Wait for the whale icon in the menu bar to stop animating"
  echo "    3. Re-run this script"
  echo ""

  # Attempt auto-launch
  echo "  Attempting to start Docker Desktop automatically..."
  open -a Docker
  echo "  Waiting up to 60s for Docker to become ready..."

  for i in $(seq 1 12); do
    sleep 5
    if nc -z -U "$SOCKET" 2>/dev/null; then
      echo "  ✅  Docker is ready."
      break
    fi
    echo "  ... still waiting ($((i * 5))s)"
    if [ "$i" -eq 12 ]; then
      echo ""
      echo "  ❌  Docker did not become ready in 60s. Please start it manually."
      exit 1
    fi
  done
else
  echo "  ✅  Docker daemon is running."
fi

# ── 2. Set correct context ─────────────────────────────────────────────────
echo "▶  Setting Docker context to desktop-linux..."
docker context use desktop-linux 2>/dev/null || true

# ── 3. Verify .env exists ─────────────────────────────────────────────────
if [ ! -f "$SCRIPT_DIR/.env" ]; then
  echo ""
  echo "  ⚠️   .env not found — copying from .env.example"
  cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
  echo "  ⚠️   Fill in real secrets in .env before using auth features."
fi

# ── 4. Build and run ───────────────────────────────────────────────────────
echo "▶  Building and starting all services..."
echo ""
cd "$SCRIPT_DIR"
docker compose up --build "$@"
