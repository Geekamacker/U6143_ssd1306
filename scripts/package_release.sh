#!/usr/bin/env bash
# Package only the Raspberry Pi source and installers (no Windows demo files).
set -euo pipefail
REPO_ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
OUTPUT_DIR="${1:-$REPO_ROOT/dist}"
mkdir -p "$OUTPUT_DIR"
OUTPUT_DIR=$(cd -- "$OUTPUT_DIR" && pwd -P)
TMP=$(mktemp -d)
trap 'rm -rf -- "$TMP"' EXIT
ROOT="$TMP/U6143_ssd1306"
mkdir -p "$ROOT/C"
cp -- "$REPO_ROOT/README.md" "$REPO_ROOT/setup_display_service.sh" \
  "$REPO_ROOT/boot_diagnostics.sh" "$REPO_ROOT/install_release.sh" "$ROOT/"
cp -- "$REPO_ROOT"/C/*.c "$REPO_ROOT"/C/*.h \
  "$REPO_ROOT"/C/Makefile "$REPO_ROOT"/C/README.md "$ROOT/C/"
ARCHIVE="$OUTPUT_DIR/U6143_ssd1306-rpi.tar.gz"
tar -czf "$ARCHIVE" -C "$TMP" U6143_ssd1306
(
    cd "$OUTPUT_DIR"
    sha256sum "$(basename "$ARCHIVE")" > "$(basename "$ARCHIVE").sha256"
)
echo "Created $ARCHIVE"
