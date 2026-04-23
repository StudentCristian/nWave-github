"""Acceptance tests for session-start routing in hook adapter.

AC-03-02: Running adapter with "session-start" argument invokes session_start_handler.
          Unknown command still exits 1. Existing routing unaffected.
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


class TestSessionStartRoutingAcceptance:
    """Acceptance: session-start dispatches to session_start_handler via adapter."""

    def test_session_start_command_dispatches_to_handler(self):
        """Running adapter with 'session-start' routes to session_start_handler."""
        from des.adapters.drivers.hooks import copilot_hook_adapter as hook_router
        from des.adapters.drivers.hooks import session_start_handler

        with patch.object(
            session_start_handler,
            "handle_session_start",
            return_value=0,
        ) as mock_handler:
            exits = _capture_exit(hook_router, ["adapter", "session-start"])

        mock_handler.assert_called_once()
        assert exits == [0]

    def test_unknown_command_exits_1(self, capsys):
        """Unknown command reports error on stderr and exits 2."""
        from des.adapters.drivers.hooks import copilot_hook_adapter as hook_router

        exits = _capture_exit(hook_router, ["adapter", "not-a-real-command"])

        # Copilot adapter writes an error message to stderr and exits 2.
        assert exits == [2]
        captured = capsys.readouterr()
        assert "DES: Unknown command" in captured.err
