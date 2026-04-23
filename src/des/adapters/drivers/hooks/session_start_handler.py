"""SessionStart hook handler for nWave housekeeping.

Reads hook input JSON from stdin, runs housekeeping tasks
(audit log rotation, stale signal cleanup, skill log trimming).

Fail-open: any exception exits 0 so session is never blocked.

Output format when housekeeping completes:
    No stdout output (housekeeping is silent).
"""

from __future__ import annotations

import sys


def _run_housekeeping(des_config) -> None:
    """Run housekeeping using configuration from DESConfig.

    Builds HousekeepingConfig from des_config properties and delegates to
    HousekeepingService. Fail-open: caller must wrap in try/except.
    """
    from des.adapters.driven.time.system_time import SystemTimeProvider
    from des.application.housekeeping_service import (
        HousekeepingConfig,
        HousekeepingService,
    )

    config = HousekeepingConfig(
        enabled=des_config.housekeeping_enabled,
        audit_retention_days=des_config.housekeeping_audit_retention_days,
        signal_staleness_hours=des_config.housekeeping_signal_staleness_hours,
        skill_log_max_bytes=des_config.housekeeping_skill_log_max_bytes,
    )
    HousekeepingService.run_housekeeping(config, SystemTimeProvider())


def handle_session_start() -> int:
    """Handle session-start hook: run housekeeping.

    Reads JSON from stdin (Copilot hook protocol), runs housekeeping.
    No update-check (removed for GitHub Copilot adaptation).

    Returns:
        0 always (fail-open: session must never be blocked).
    """
    sys.stdin.read()

    from des.adapters.driven.config.des_config import DESConfig

    des_config = DESConfig()

    try:
        _run_housekeeping(des_config)
    except Exception:
        pass

    return 0
