"""
DES Configuration Adapter - Driven Port Implementation.

Loads configuration from .nwave/des-config.json and provides access to settings.
Falls back to safe defaults (audit logging ON) when file is missing or invalid.

Rigor cascade: project config -> global config -> standard defaults.
When a project has a "rigor" key, the entire global rigor block is ignored.

Hexagonal Architecture:
- DRIVEN ADAPTER: Implements configuration port (driven by business logic)
- ON BY DEFAULT: Audit logging enabled unless explicitly disabled in config
"""

import json
import os
from pathlib import Path
from typing import Any

from des.domain.nwave_dir_gitignore import ensure_nwave_gitignore


class DESConfig:
    """
    Configuration loader for DES settings.

    Loads configuration from .nwave/des-config.json with on-by-default audit logging.
    Supports global configuration via ~/.nwave/global-config.json for cross-project
    rigor preferences. Does NOT auto-create config files.

    Rigor cascade: project rigor -> global rigor -> standard defaults.
    """

    _DEFAULT_GLOBAL_CONFIG_PATH = Path.home() / ".nwave" / "global-config.json"

    def __init__(
        self,
        config_path: Path | None = None,
        cwd: Path | None = None,
        *,
        global_config_path: Path | None = None,
    ):
        """
        Initialize DESConfig.

        Args:
            config_path: Optional explicit path to project config file
            cwd: Optional working directory (defaults to Path.cwd());
                 used to resolve .nwave/des-config.json when config_path is None
            global_config_path: Optional explicit path to global config file
                (keyword-only; defaults to ~/.nwave/global-config.json)
        """
        if config_path is None:
            effective_cwd = cwd or Path.cwd()
            config_path = effective_cwd / ".nwave" / "des-config.json"

        self._config_path = config_path
        self._config_data = self._load_json_file(self._config_path)

        effective_global_path = (
            global_config_path
            if global_config_path is not None
            else self._DEFAULT_GLOBAL_CONFIG_PATH
        )
        self._global_config_data = self._load_json_file(effective_global_path)

    @staticmethod
    def _load_json_file(path: Path) -> dict[str, Any]:
        """
        Load configuration from a JSON file.

        Returns empty dict when the file is missing, corrupt, or unreadable.
        Pure function: no side effects beyond filesystem read.

        Args:
            path: Path to the JSON file to load

        Returns:
            Configuration dictionary, empty dict if loading fails
        """
        if not path.exists():
            return {}

        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    @property
    def skill_tracking_enabled(self) -> bool:
        """
        Check if skill loading tracking is enabled.

        Priority: DES_SKILL_TRACKING env var > config file > default (False).

        Returns:
            True if skill tracking enabled, False otherwise (defaults to False)
        """
        env_override = os.environ.get("DES_SKILL_TRACKING")
        if env_override is not None:
            return env_override.lower() in ("true", "1", "yes")
        strategy = self._config_data.get("skill_tracking", "disabled")
        return strategy != "disabled"

    @property
    def skill_tracking_strategy(self) -> str:
        """
        Get skill tracking strategy.

        Returns:
            Strategy string: "disabled", "passive-logging", or "token-tracking"
        """
        return self._config_data.get("skill_tracking", "disabled")

    @property
    def audit_logging_enabled(self) -> bool:
        """
        Check if audit logging is enabled.

        Priority: DES_AUDIT_LOGGING_ENABLED env var > config file > default (True).

        Returns:
            True if audit logging enabled, False otherwise (defaults to True)
        """
        env_override = os.environ.get("DES_AUDIT_LOGGING_ENABLED")
        if env_override is not None:
            return env_override.lower() in ("true", "1", "yes")
        return self._config_data.get("audit_logging_enabled", True)

    def _rigor(self) -> dict:
        """Return rigor sub-config via cascade: project -> global -> empty dict.

        When the project config contains a "rigor" key (even if empty),
        the entire global rigor block is ignored -- full block override.
        """
        if "rigor" in self._config_data:
            return self._config_data["rigor"]
        return self._global_config_data.get("rigor", {})

    # Auto-update configuration removed for Copilot migration. Update
    # management is out-of-scope for the DES runtime under Copilot.

    def _housekeeping(self) -> dict:
        """Return housekeeping sub-config dict, defaulting to empty dict."""
        return self._config_data.get("housekeeping", {})

    @property
    def rigor_profile(self) -> str:
        """Get rigor profile name. Default: 'standard'."""
        return self._rigor().get("profile", "standard")

    @property
    def rigor_agent_model(self) -> str:
        """Get agent model from rigor config. Default: 'sonnet'."""
        return self._rigor().get("agent_model", "sonnet")

    @property
    def rigor_reviewer_model(self) -> str:
        """Get reviewer model. Default: 'haiku'."""
        return self._rigor().get("reviewer_model", "haiku")

    @property
    def rigor_tdd_phases(self) -> tuple[str, ...]:
        """Get TDD phases as tuple. Default: full 5-phase."""
        phases = self._rigor().get(
            "tdd_phases",
            ["PREPARE", "RED_ACCEPTANCE", "RED_UNIT", "GREEN", "COMMIT"],
        )
        return tuple(phases)

    @property
    def rigor_review_enabled(self) -> bool:
        """Check if peer review is enabled. Default: True."""
        return self._rigor().get("review_enabled", True)

    @property
    def rigor_double_review(self) -> bool:
        """Check if double review is enabled. Default: False."""
        return self._rigor().get("double_review", False)

    @property
    def rigor_mutation_enabled(self) -> bool:
        """Check if mutation testing is enabled. Default: False."""
        return self._rigor().get("mutation_enabled", False)

    @property
    def rigor_refactor_pass(self) -> bool:
        """Check if refactoring pass is enabled. Default: True."""
        return self._rigor().get("refactor_pass", True)
    # update_check properties removed: auto-update is out-of-scope

    @property
    def housekeeping_enabled(self) -> bool:
        """Check if housekeeping is enabled. Default: True."""
        return self._housekeeping().get("enabled", True)

    @property
    def housekeeping_audit_retention_days(self) -> int:
        """Get audit log retention period in days. Default: 7."""
        return self._housekeeping().get("audit_retention_days", 7)

    @property
    def housekeeping_signal_staleness_hours(self) -> int:
        """Get signal file staleness threshold in hours. Default: 4."""
        return self._housekeeping().get("signal_staleness_hours", 4)

    @property
    def housekeeping_skill_log_max_bytes(self) -> int:
        """Get maximum skill log size in bytes before rotation. Default: 1 MiB."""
        return self._housekeeping().get("skill_log_max_bytes", 1_048_576)

    # --- Observability (NWave unified logging) ---

    @property
    def log_level(self) -> str:
        """Log level: NW_LOG_LEVEL env > config log_level > default WARN."""
        env = os.environ.get("NW_LOG_LEVEL")
        if env:
            return env.upper()
        return self._config_data.get("log_level", "WARN").upper()

    @property
    def log_enabled(self) -> bool:
        """Log enabled: NW_LOG env > config log_enabled > default False."""
        env = os.environ.get("NW_LOG")
        if env is not None:
            return env.lower() in ("true", "1", "yes")
        return bool(self._config_data.get("log_enabled", False))

    # Note: update check persistence APIs removed. Update lifecycle is
    # managed outside of DES runtime when running under GitHub Copilot.
