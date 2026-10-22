from pathlib import Path
import tempfile, os, subprocess, textwrap
script = str(Path(__file__).resolve().parents[1] / 'boot_diagnostics.sh')
with tempfile.TemporaryDirectory() as d:
    p = Path(d)
    (p/'bin').mkdir(); (p/'state').mkdir()
    (p/'boot_id').write_text('boot-A\n')
    # fake journal for previous boot tests
    fake=p/'bin/journalctl'; fake.write_text('''#!/usr/bin/env bash
case "$*" in
  *--boot=*)
  if [ "${SCENARIO:-}" = "sd" ]; then
    echo '1792701000.100000 host kernel: mmc0: cmd error -110 waiting'
    echo '1792701050.100000 host systemd: latest logged activity'
  elif [ "${SCENARIO:-}" = "old" ]; then
    echo '1792690000.100000 host kernel: mmc0: cmd error -110 waiting'
    echo '1792701050.100000 host cron: latest logged activity'
  elif [ "${SCENARIO:-}" = "panic" ]; then
    echo '1792701000.100000 host kernel: Kernel panic - not syncing'
    echo '1792701050.100000 host kernel: latest'
  elif [ "${SCENARIO:-}" = "no-journal" ]; then
    exit 1
  else
    echo '1792701050.100000 host cron: clean last activity'
  fi
  ;;
  *) exit 1 ;;
esac
'''); fake.chmod(0o755)
    env={**os.environ,'UCTRONICS_STATE_DIR':str(p/'state'), 'UCTRONICS_BOOT_ID_FILE':str(p/'boot_id'), 'PATH':str(p/'bin')+':'+os.environ['PATH']}
    def cmd(a,sc=None):
        e=env.copy(); e['SCENARIO']=sc or ''
        subprocess.run(['bash',script,a],env=e,check=True,capture_output=True,text=True)
        return (p/'state/last_boot_status').read_text() if (p/'state/last_boot_status').exists() else ''
    print('first-install:',repr(cmd('start')))
    assert 'PREV: UNTRACKED' in (p/'state/last_boot_status').read_text()
    cmd('stop'); (p/'boot_id').write_text('boot-B\n')
    print('clean-reboot:',repr(cmd('start')))
    assert 'PREV: CLEAN' in (p/'state/last_boot_status').read_text()
    (p/'boot_id').write_text('boot-C\n')
    print('unexpected-reboot w/ SD error:',repr(cmd('start','sd')))
    assert 'PREV: UNCLEAN' in (p/'state/last_boot_status').read_text()
    assert 'LOG: MMC ERROR' in (p/'state/last_boot_status').read_text()
    (p/'boot_id').write_text('boot-D\n')
    print('no journal clue:',repr(cmd('start')))
    assert 'LOG: NO CAUSE' in (p/'state/last_boot_status').read_text()
    (p/'boot_id').write_text('boot-E\n')
    print('stale error excluded:',repr(cmd('start','old')))
    assert 'LOG: NO CAUSE' in (p/'state/last_boot_status').read_text()
    (p/'boot_id').write_text('boot-F\n')
    print('kernel panic recognized:',repr(cmd('start','panic')))
    assert 'LOG: PANIC/HANG' in (p/'state/last_boot_status').read_text()
    (p/'boot_id').write_text('boot-G\n')
    print('no journal:',repr(cmd('start','no-journal')))
    assert 'LOG: NOT SAVED' in (p/'state/last_boot_status').read_text()
    # same boot restart must not overwrite previous findings
    print('restart same boot:',repr(cmd('start')))
    assert 'LOG: NOT SAVED' in (p/'state/last_boot_status').read_text()
    print('All simulations passed')
