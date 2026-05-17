#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -x ".venv/bin/python" ]; then
  echo "Creando entorno virtual en .venv..."
  python3 -m venv .venv
fi

if ! .venv/bin/python -c "import fastapi, uvicorn" >/dev/null 2>&1; then
  echo "Instalando dependencias..."
  .venv/bin/python -m pip install -r requirements.txt
fi

exec .venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
