"""Unit tests for `handle_session_start()` after Copilot migration.

These tests verify that session-start runs housekeeping and is fail-open.
Housekeeping is the only behavior retained by the handler.
"""

import io
from unittest.mock import MagicMock, patch


def test_handle_session_start_calls_run_housekeeping_and_returns_0():
    from des.adapters.drivers.hooks.session_start_handler import (
        handle_session_start,
    )

    with (
        patch(
            "des.adapters.drivers.hooks.session_start_handler._run_housekeeping"
        ) as mock_hk,
        patch("sys.stdin", io.StringIO("{}")),
    ):
        exit_code = handle_session_start()

    assert exit_code == 0
    mock_hk.assert_called_once()


def test_housekeeping_failure_is_fail_open_and_no_stdout(capsys):
    from des.adapters.drivers.hooks.session_start_handler import (
        handle_session_start,
    )

    with (
        patch(
            "des.adapters.drivers.hooks.session_start_handler._run_housekeeping",
            side_effect=RuntimeError("housekeeping failed"),
        ),
        patch("sys.stdin", io.StringIO("{}")),
    ):
        exit_code = handle_session_start()

    assert exit_code == 0
    assert capsys.readouterr().out.strip() == ""


def test_empty_stdin_still_runs_housekeeping_and_returns_0():
    from des.adapters.drivers.hooks.session_start_handler import (
        handle_session_start,
    )

    with (
        patch(
            "des.adapters.drivers.hooks.session_start_handler._run_housekeeping"
        ) as mock_hk,
        patch("sys.stdin", io.StringIO("")),
    ):
        exit_code = handle_session_start()

    assert exit_code == 0
    mock_hk.assert_called_once()


def test_handle_session_start_produces_no_stdout_on_success(capsys):
    from des.adapters.drivers.hooks.session_start_handler import (
        handle_session_start,
    )

    with (
        patch(
            "des.adapters.drivers.hooks.session_start_handler._run_housekeeping"
        ) as mock_hk,
        patch("sys.stdin", io.StringIO("{}")),
    ):
        exit_code = handle_session_start()

    assert exit_code == 0
    assert capsys.readouterr().out.strip() == ""
