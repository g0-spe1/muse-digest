#!/usr/bin/env bash
# ============================================================
#  MuseDigest iOS gallery launcher (macOS / Linux)
#  Renders the existing library into a mobile/iOS-optimized,
#  self-contained gallery. No GPU, no re-analysis.
#
#    ./start-ios.sh            build + open in browser
#    ./start-ios.sh --serve    also start a LAN server so an iPhone
#                             on the same WiFi can open it in Safari
# ============================================================
set -euo pipefail
cd "$(dirname "$0")"

# Prefer the parent repo's .venv if present (mirrors start.bat).
if [ -x "../.venv/bin/python" ]; then
  PY="../.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PY="python3"
else
  PY="python"
fi

"$PY" build_ios_gallery.py --open "$@"
