# Local companion restart and recovery proof

Date: 2026-08-13
Checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
Evidence tier: Tier 4 local runtime observation

## Command

```text
SIGNKIT_DATA_DIR="$PWD/.codex-test-tmp/companion-restart-data-2" \
  ./.venv/bin/python -c 'from desktop_app.backend_manager import BackendManager; m=BackendManager(port=8124, auto_start=True); first=m.start(); first_health=m.is_available(); restarted=m.restart(); second_health=m.is_available(); second_status=m.get_status(); m.shutdown(); stopped=(m.process is None and not m.is_available()); print({"first_start": first, "first_health": first_health, "restarted": restarted, "second_health": second_health, "second_status": second_status, "stopped_cleanly": stopped}); assert first and first_health and restarted and second_health and stopped'
```

## Observed result

The real local `BackendManager` started a disposable companion on port `8124`,
passed the health proof, restarted the process, passed the health proof again,
and shut down without leaving a managed process or a health response:

```text
{
  'first_start': True,
  'first_health': True,
  'restarted': True,
  'second_health': True,
  'second_status': {
    'available': True,
    'process_running': True,
    'port': 8124,
    'auto_start': True,
    'startup_attempts': 2,
    'pid': 29140
  },
  'stopped_cleanly': True
}
```

The data directory was disposable and ignored under `.codex-test-tmp/`. No
hosted service was used and no document bytes crossed the local companion
boundary in this proof.

## Scope boundary

This closes the local process start/restart/health/shutdown observation for the
current macOS development runtime. It does not prove packaged-runtime outage
recovery, cross-platform process supervision, assistive-technology behavior,
target deployment, or hosted availability.
