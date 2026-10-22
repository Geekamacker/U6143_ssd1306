#!/usr/bin/env bash
# Lightweight previous-boot diagnostic recorder for UCTRONICS OLED.
# Detects whether systemd had a chance to stop this unit cleanly.
# NEVER claims an exact crash cause: a journal keyword is only a clue.
set -euo pipefail

STATE_DIR="${UCTRONICS_STATE_DIR:-/var/lib/uctronics-display}"
BOOT_ID_FILE="${UCTRONICS_BOOT_ID_FILE:-/proc/sys/kernel/random/boot_id}"
MARKER="$STATE_DIR/boot_state"
STATUS_FILE="$STATE_DIR/last_boot_status"
DETAILS_FILE="$STATE_DIR/last_boot_report.txt"

atomic_write() {
    local destination="$1"
    local tmp
    tmp=$(mktemp "${destination}.XXXXXX")
    cat > "$tmp"
    chmod 0644 "$tmp"
    mv -f "$tmp" "$destination"
}

read_previous_marker() {
    prev_id=""
    prev_state=""
    if [[ -f "$MARKER" ]]; then
        read -r prev_id prev_state < "$MARKER" || true
    fi
}

# Search only the hour preceding the LAST SAVED journal message of the
# previous boot. A log hit is a clue, not proof of the root cause.
inspect_previous_journal() {
    clue='LOG: NO CAUSE'
    evidence='No matching failure signature was captured.'
    last_entry='Unknown'

    local all recent epoch cutoff candidate
    all=$(mktemp)
    recent=$(mktemp)
    if ! journalctl --quiet --boot="$prev_id" --no-pager \
            -o short-unix -n 2000 > "$all" 2>/dev/null || [[ ! -s "$all" ]]; then
        clue='LOG: NOT SAVED'
        evidence='No accessible journal entries for the previous boot.'
        rm -f "$all" "$recent"
        return
    fi

    epoch=$(awk '$1 ~ /^[0-9]+\.[0-9]+$/ { t=int($1) } END { if (t) print t }' "$all")
    if [[ -z "$epoch" ]]; then
        clue='LOG: NOT SAVED'
        evidence='Previous-boot journal has no usable timestamps.'
        rm -f "$all" "$recent"
        return
    fi

    last_entry=$(date -d "@$epoch" '+%Y-%m-%d %H:%M:%S %z')
    cutoff=$((epoch - 3600))
    awk -v minimum="$cutoff" '$1 ~ /^[0-9]+\.[0-9]+$/ && int($1) >= minimum' \
        "$all" > "$recent"

    # Priority reflects diagnostic specificity, not certainty of causation.
    # Avoid incidental strings such as the watchdog initialization message.
    choose_clue() {
        local label="$1" pattern="$2"
        candidate=$(grep -Ei -- "$pattern" "$recent" | tail -n 1 || true)
        if [[ -n "$candidate" ]]; then
            clue="LOG: $label"
            evidence="$candidate"
            return 0
        fi
        return 1
    }

    if choose_clue 'PANIC/HANG' 'Kernel panic|BUG:.*(lockup|scheduling)|soft lockup|hard LOCKUP|rcu.*stall|task .* blocked for more than'; then :
    elif choose_clue 'MMC ERROR' 'cmd error -110|mmc[0-9:].*(error|timeout|failed|timed out)|mmcblk.*(error|timeout)|I/O error.*mmcblk|Buffer I/O error.*mmc'; then :
    elif choose_clue 'EXT4 ERROR' 'EXT4-fs error|JBD2.*(error|aborted)|Remounting filesystem read-only'; then :
    elif choose_clue 'UNDERVOLT' 'under.voltage|voltage.*(too low|low detected)|brownout'; then :
    elif choose_clue 'OVERHEAT' 'thermal.*(critical|shutdown)|critical temperature'; then :
    elif choose_clue 'OOM EVENT' 'out of memory:|oom-killer|oom_reaper|Killed process.*total-vm'; then :
    elif choose_clue 'WATCHDOG' 'watchdog.*(pretimeout|expired|reset due|did not stop)'; then :
    fi
    rm -f "$all" "$recent"
}

case "${1:-}" in
    start)
        mkdir -p "$STATE_DIR"
        current_id=$(cat "$BOOT_ID_FILE")
        read_previous_marker

        # Restarting the diagnostic unit in the same boot must not invent a
        # new crash or overwrite the previous-boot evidence report.
        if [[ "$prev_id" == "$current_id" ]]; then
            printf '%s RUNNING\n' "$current_id" | atomic_write "$MARKER"
            exit 0
        fi

        if [[ -z "$prev_id" ]]; then
            previous='PREV: UNTRACKED'
            clue='LOG: NO BASELINE'
            evidence='First monitored boot; no shutdown marker from a previous run.'
            last_entry='Unknown'
        elif [[ "$prev_state" == 'CLEAN' ]]; then
            previous='PREV: CLEAN'
            clue='LOG: N/A'
            evidence='The diagnostic service stopped normally in the previous boot.'
            last_entry='N/A'
        else
            previous='PREV: UNCLEAN'
            inspect_previous_journal
        fi

        printf '%s\n%s\n' "$previous" "$clue" | atomic_write "$STATUS_FILE"
        {
            printf 'Previous boot ID: %s\n' "${prev_id:-Unavailable}"
            printf 'Previous marker: %s\n' "${prev_state:-Unavailable}"
            printf 'Last saved journal entry: %s\n' "$last_entry"
            printf 'OLED: %s / %s\n' "$previous" "$clue"
            printf 'Evidence: %s\n' "$evidence"
            printf '\nCaution: UNCLEAN means no orderly service stop was recorded.\n'
            printf 'A LOG clue is a matching journal event, not a proven cause.\n'
            printf 'NO CAUSE means the final failure was not captured.\n'
        } | atomic_write "$DETAILS_FILE"
        printf '%s RUNNING\n' "$current_id" | atomic_write "$MARKER"
        ;;
    stop)
        # Called by systemd during an orderly stop/reboot/shutdown.
        # A hard freeze or power loss cannot reach this command.
        [[ -f "$MARKER" ]] || exit 0
        current_id=$(cat "$BOOT_ID_FILE")
        read_previous_marker
        if [[ "$prev_id" == "$current_id" ]]; then
            printf '%s CLEAN\n' "$current_id" | atomic_write "$MARKER"
        fi
        ;;
    report)
        if [[ -f "$DETAILS_FILE" ]]; then cat "$DETAILS_FILE"; else
            echo 'No baseline yet. Install and start the diagnostic systemd service.'
        fi
        ;;
    *)
        echo 'Usage: boot_diagnostics.sh {start|stop|report}' >&2
        exit 2
        ;;
esac
