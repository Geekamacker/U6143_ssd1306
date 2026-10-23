#!/usr/bin/env bash
# Offline smoke test for the release downloader. Does not call sudo or GitHub.
set -euo pipefail
BASE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/bin" "$TMP/home" "$TMP/assets"
bash "$BASE/scripts/package_release.sh" "$TMP/assets" >/dev/null
cat > "$TMP/bin/curl" <<'MOCK'
#!/usr/bin/env bash
set -euo pipefail
outfile=""
url=""
while (($#)); do
  case "$1" in
    -o) outfile="$2"; shift 2 ;;
    -H) shift 2 ;;
    -*) shift ;;
    *) url="$1"; shift ;;
  esac
done
if [[ "$url" == *'/releases/latest' ]]; then
  printf '%s\n' '{"tag_name":"v1.2.3"}'
elif [[ "$url" == *'.sha256' ]]; then
  cp -- "${FAKE_RELEASE_ASSETS}/U6143_ssd1306-rpi.tar.gz.sha256" "$outfile"
elif [[ "$url" == *'U6143_ssd1306-rpi.tar.gz' ]]; then
  cp -- "${FAKE_RELEASE_ASSETS}/U6143_ssd1306-rpi.tar.gz" "$outfile"
else
  echo "Unexpected URL: $url" >&2
  exit 1
fi
MOCK
chmod +x "$TMP/bin/curl"
export HOME="$TMP/home" PATH="$TMP/bin:$PATH" FAKE_RELEASE_ASSETS="$TMP/assets"
bash "$BASE/install_release.sh" --no-install
[[ -f "$HOME/.local/share/uctronics-display/releases/v1.2.3/C/Makefile" ]]
[[ -f "$HOME/.local/share/uctronics-display/releases/v1.2.3/.release_sha256" ]]
bash "$BASE/install_release.sh" --tag v1.2.3 --no-install
echo 'Release downloader offline smoke test passed'
