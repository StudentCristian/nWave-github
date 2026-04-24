"""Unit tests for session-start routing in copilot_hook_adapter.

Test budget: 3 behaviors x 2 = 6 unit tests max.
"""

import json
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


class TestSessionStartRouting:
    """B1: 'session-start' argument routes to handle_session_start."""

    def test_session_start_calls_handle_session_start(self):
        """session-start command dispatches to handle_session_start."""
        from des.adapters.drivers.hooks import copilot_hook_adapter as hook_router
        from des.adapters.drivers.hooks import session_start_handler

        with patch.object(
            session_start_handler,
            "handle_session_start",
            return_value=0,
        ) as mock_handler:
            _capture_exit(hook_router, ["adapter", "session-start"])

        mock_handler.assert_called_once()

    def test_session_start_exit_code_from_handler(self):
        """session-start forwards handler return value as exit code."""
        from des.adapters.drivers.hooks import copilot_hook_adapter as hook_router
        from des.adapters.drivers.hooks import session_start_handler

        with patch.object(
            session_start_handler,
            "handle_session_start",
            return_value=0,
        ):
            exits = _capture_exit(hook_router, ["adapter", "session-start"])

        assert exits == [0]


class TestUnknownCommandExits2:
    """B2: Unknown command exits 2."""

    def test_unknown_command_exits_2(self, capsys):
        """Unknown command exits 2 with error on stderr."""
        from des.adapters.drivers.hooks import copilot_hook_adapter as hook_router

        exits = _capture_exit(hook_router, ["adapter", "totally-unknown-xyz"])

        assert exits == [2]
        err = capsys.readouterr().err.strip()
        assert "totally-unknown-xyz" in err


class TestExistingRoutingUnaffected:
    """B3: Existing routing (pre-tool-use, subagent-stop, post-tool-use) unaffected."""

    def test_pre_tool_use_still_routes_to_pre_tool_use_handler(self):
        """pre-tool-use command still routes to handle_pre_tool_use."""
        from des.adapters.drivers.hooks import copilot_hook_adapter as hook_router
        from des.adapters.drivers.hooks import pre_tool_use_handler

        with patch.object(
            pre_tool_use_handler,
            "handle_pre_tool_use",
            return_value=0,
        ) as mock_handler:
            _capture_exit(hook_router, ["adapter", "pre-tool-use"])

        mock_handler.assert_called_once()
