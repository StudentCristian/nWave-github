"""Unit tests for deliver-progress hook registration and routing.

Step 01-02: Register deliver-progress as second SubagentStop hook event
and wire router dispatch.

Test Budget: 3 behaviors x 2 = 6 unit tests max.
Behaviors:
  B1: HOOK_EVENTS has 2 SubagentStop entries with correct actions/matchers
  B2: Router dispatches deliver-progress to handle_deliver_progress
  B3: generate_hook_config produces 2 SubagentStop entries without matcher
"""

from __future__ import annotations

import sys
from unittest.mock import patch


def _capture_exit(module, argv):
    """Run module.main() with patched argv and capture exit code."""
    exits = []

    def fake_exit(code):
        exits.append(code)

    with patch("sys.argv", argv), patch.object(sys, "exit", fake_exit):
        module.main()

    return exits


class TestHookEventsSubagentStopEntries:
    """B1: HOOK_EVENTS has exactly 2 SubagentStop entries."""

    def test_two_subagent_stop_entries_exist(self):
        """HOOK_EVENTS contains exactly 2 SubagentStop entries."""
        from scripts.shared.hook_definitions import HOOK_EVENTS

        subagent_stop_events = [h for h in HOOK_EVENTS if h.event == "SubagentStop"]
        assert len(subagent_stop_events) == 2

    def test_subagent_stop_actions_are_correct(self):
        """SubagentStop entries have actions 'subagent-stop' and 'deliver-progress'."""
        from scripts.shared.hook_definitions import HOOK_EVENTS

        subagent_stop_events = [h for h in HOOK_EVENTS if h.event == "SubagentStop"]
        actions = [h.action for h in subagent_stop_events]
        assert actions == ["subagent-stop", "deliver-progress"]

    def test_subagent_stop_entries_have_no_matcher(self):
        """Both SubagentStop entries have matcher=None."""
        from scripts.shared.hook_definitions import HOOK_EVENTS

        subagent_stop_events = [h for h in HOOK_EVENTS if h.event == "SubagentStop"]
        assert all(h.matcher is None for h in subagent_stop_events)


class TestRouterDeliverProgressDispatch:
    """B2: Router dispatches deliver-progress to handle_deliver_progress."""

    def test_deliver_progress_routes_to_handler(self):
        """deliver-progress command dispatches to handle_deliver_progress."""
        from des.adapters.drivers.hooks import hook_router

        with patch.object(
            hook_router,
            "handle_deliver_progress",
            return_value=0,
        ) as mock_handler:
            _capture_exit(hook_router, ["adapter", "deliver-progress"])

        mock_handler.assert_called_once()

    def test_deliver_progress_returns_exit_code_0(self):
        """deliver-progress forwards handler return value as exit code."""
        from des.adapters.drivers.hooks import hook_router

        with patch.object(
            hook_router,
            "handle_deliver_progress",
            return_value=0,
        ):
            exits = _capture_exit(hook_router, ["adapter", "deliver-progress"])

        assert exits == [0]


class TestGenerateHookConfigSubagentStop:
    """B3: generate_hook_config produces 2 SubagentStop entries without matcher."""

    def test_config_has_two_subagent_stop_hooks(self):
        """SubagentStop list in generated config contains exactly 2 entries."""
        from scripts.shared.hook_definitions import generate_hook_config

        config = generate_hook_config(command_fn=lambda action: f"cmd {action}")
        subagent_stop_entries = config["SubagentStop"]
        assert len(subagent_stop_entries) == 2

        # Neither entry has a matcher field
        for entry in subagent_stop_entries:
            assert "matcher" not in entry

        # Verify correct action commands are wired
        commands = [entry["hooks"][0]["command"] for entry in subagent_stop_entries]
        assert commands == ["cmd subagent-stop", "cmd deliver-progress"]
