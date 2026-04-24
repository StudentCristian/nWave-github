"""Tests for decision logging in handle_pre_write.

handle_pre_write emits HOOK_PRE_WRITE_ALLOWED or HOOK_PRE_WRITE_BLOCKED audit
events after the SessionGuardPolicy check, and enriches HOOK_INVOKED with
input_summary including file_path, session_active, and des_task_active.

Tests exercise through the handle_pre_write driving port and assert at the
AuditLogWriter driven port boundary.

Test Budget: 8 distinct behaviors x 2 = 16 max. Using 8 tests.

Behaviors:
1. HOOK_INVOKED enriched with session_active and des_task_active in input_summary
2. HOOK_PRE_WRITE_ALLOWED emitted when session not active (reason='no_session')
3. HOOK_PRE_WRITE_ALLOWED emitted for allowed paths
4. HOOK_PRE_WRITE_BLOCKED emitted when guard blocks the write
5. Exception in decision logging does not break handler (fail-open preserved)
6. Execution log direct Write always blocked — guides to des.cli.init_log
7. Execution log direct Edit always blocked — guides to des.cli.log_phase
8. Write vs Edit block messages are different (init_log vs log_phase)
"""

import io
import json
from unittest.mock import patch

import pytest

from des.adapters.drivers.hooks import des_task_signal, hook_protocol

from .conftest import make_capturing_writer


def _build_pre_write_stdin(file_path: str = "/tmp/test.py") -> str:
    """Build create_file tool input JSON (Copilot write tool)."""
    return json.dumps({"tool_name": "create_file", "tool_input": {"filePath": file_path}})


def _build_pre_edit_stdin(file_path: str = "/tmp/test.py") -> str:
    """Build replace_string_in_file tool input JSON (Copilot edit tool)."""
    return json.dumps({"tool_name": "replace_string_in_file", "tool_input": {"filePath": file_path}})


# --- Test 1: HOOK_INVOKED enriched with session_active and des_task_active ---


def test_hook_invoked_includes_session_state_in_input_summary(monkeypatch, tmp_path):
    """HOOK_INVOKED input_summary includes file_path, session_active, and des_task_active."""
    from des.adapters.drivers.hooks import pre_write_handler as adapter

    events = []
    writer = make_capturing_writer(events)

    # Set up deliver session as active, DES task as inactive
    session_file = tmp_path / "deliver-session.json"
    session_file.write_text("{}")
    monkeypatch.setattr(des_task_signal, "DES_DELIVER_SESSION_FILE", session_file)
    monkeypatch.setattr(
        des_task_signal, "DES_TASK_ACTIVE_FILE", tmp_path / "nonexistent"
    )

    monkeypatch.setattr(
        "sys.stdin", io.StringIO(_build_pre_write_stdin("/tmp/safe.txt"))
    )
    monkeypatch.setattr("builtins.print", lambda *a, **kw: None)

    with patch.object(hook_protocol, "_audit_writer_factory", return_value=writer):
        adapter.handle_pre_write()

    invoked_events = [e for e in events if e.event_type == "HOOK_INVOKED"]
    assert len(invoked_events) >= 1, "Expected at least one HOOK_INVOKED event"

    summary = invoked_events[0].data.get("input_summary", {})
    assert "file_path" in summary, "input_summary must include file_path"
    assert "session_active" in summary, "input_summary must include session_active"
    assert "des_task_active" in summary, "input_summary must include des_task_active"
    assert summary["session_active"] is True
    assert summary["des_task_active"] is False


# --- Test 2: HOOK_PRE_WRITE_ALLOWED emitted when no session active ---


def test_allowed_event_emitted_when_no_session(monkeypatch, tmp_path):
    """HOOK_PRE_WRITE_ALLOWED emitted with reason='no_session' when no deliver session."""
    from des.adapters.drivers.hooks import pre_write_handler as adapter

    events = []
    writer = make_capturing_writer(events)

    # No session file, no DES task
    monkeypatch.setattr(
        des_task_signal, "DES_DELIVER_SESSION_FILE", tmp_path / "nonexistent"
    )
    monkeypatch.setattr(
        des_task_signal, "DES_TASK_ACTIVE_FILE", tmp_path / "nonexistent"
    )

    monkeypatch.setattr("sys.stdin", io.StringIO(_build_pre_write_stdin("src/main.py")))
    monkeypatch.setattr("builtins.print", lambda *a, **kw: None)

    with patch.object(hook_protocol, "_audit_writer_factory", return_value=writer):
        exit_code = adapter.handle_pre_write()

    assert exit_code == 0

    allowed_events = [e for e in events if e.event_type == "HOOK_PRE_WRITE_ALLOWED"]
    assert len(allowed_events) == 1, (
        f"Expected one HOOK_PRE_WRITE_ALLOWED event, got {len(allowed_events)}. "
        f"All events: {[e.event_type for e in events]}"
    )

    event = allowed_events[0]
    assert event.data["file_path"] == "src/main.py"
    assert event.data["reason"] == "no_session"


# --- Test 3: HOOK_PRE_WRITE_ALLOWED emitted for allowed/unprotected paths ---


@pytest.mark.parametrize(
    "file_path,scenario",
    [
        ("docs/feature/des-obs/plan.md", "orchestration path always allowed"),
        ("/tmp/safe.txt", "unprotected path not blocked"),
    ],
    ids=["orchestration_path", "unprotected_path"],
)
def test_allowed_event_emitted_for_non_blocked_paths(
    file_path, scenario, monkeypatch, tmp_path
):
    """HOOK_PRE_WRITE_ALLOWED emitted for paths the policy allows during active session."""
    from des.adapters.drivers.hooks import pre_write_handler as adapter

    events = []
    writer = make_capturing_writer(events)

    # Session active but no DES task
    session_file = tmp_path / "deliver-session.json"
    session_file.write_text("{}")
    monkeypatch.setattr(des_task_signal, "DES_DELIVER_SESSION_FILE", session_file)
    monkeypatch.setattr(
        des_task_signal, "DES_TASK_ACTIVE_FILE", tmp_path / "nonexistent"
    )

    monkeypatch.setattr("sys.stdin", io.StringIO(_build_pre_write_stdin(file_path)))
    monkeypatch.setattr("builtins.print", lambda *a, **kw: None)

    with patch.object(hook_protocol, "_audit_writer_factory", return_value=writer):
        exit_code = adapter.handle_pre_write()

    assert exit_code == 0

    allowed_events = [e for e in events if e.event_type == "HOOK_PRE_WRITE_ALLOWED"]
    assert len(allowed_events) == 1, (
        f"Expected HOOK_PRE_WRITE_ALLOWED for '{scenario}', "
        f"got events: {[e.event_type for e in events]}"
    )
    assert allowed_events[0].data["file_path"] == file_path


# --- Test 4: HOOK_PRE_WRITE_BLOCKED emitted when guard blocks ---


def test_blocked_event_emitted_when_guard_blocks(monkeypatch, tmp_path):
    """HOOK_PRE_WRITE_BLOCKED emitted with file_path and reason when source write blocked."""
    from des.adapters.drivers.hooks import pre_write_handler as adapter

    events = []
    writer = make_capturing_writer(events)

    # Session active, no DES task, writing to protected path
    session_file = tmp_path / "deliver-session.json"
    session_file.write_text("{}")
    monkeypatch.setattr(des_task_signal, "DES_DELIVER_SESSION_FILE", session_file)
    monkeypatch.setattr(
        des_task_signal, "DES_TASK_ACTIVE_FILE", tmp_path / "nonexistent"
    )

    monkeypatch.setattr(
        "sys.stdin", io.StringIO(_build_pre_write_stdin("src/des/main.py"))
    )
    printed = []
    monkeypatch.setattr("builtins.print", lambda *a, **kw: printed.append(a))

    with patch.object(hook_protocol, "_audit_writer_factory", return_value=writer):
        exit_code = adapter.handle_pre_write()

    assert exit_code == 0

    # Verify Copilot block response structure
    assert len(printed) >= 1, "Expected block response on stdout"
    response_json = json.loads(printed[-1][0])
    hook_output = response_json["hookSpecificOutput"]
    assert hook_output["permissionDecision"] == "deny"
    assert hook_output["permissionDecisionReason"]

    blocked_events = [e for e in events if e.event_type == "HOOK_PRE_WRITE_BLOCKED"]
    assert len(blocked_events) == 1, (
        f"Expected one HOOK_PRE_WRITE_BLOCKED event, got {len(blocked_events)}. "
        f"All events: {[e.event_type for e in events]}"
    )

    event = blocked_events[0]
    assert event.data["file_path"] == "src/des/main.py"
    assert "reason" in event.data
    assert len(event.data["reason"]) > 0, "Blocked reason must not be empty"
    assert "hook_id" in event.data, "HOOK_PRE_WRITE_BLOCKED must include hook_id"


# --- Test 5: Exception in decision logging does not break fail-open behavior ---


def test_logging_exception_preserves_fail_open_behavior(monkeypatch, tmp_path):
    """When audit logging raises, handle_pre_write still returns allow (fail-open)."""
    from des.adapters.drivers.hooks import pre_write_handler as adapter

    call_count = 0

    class ExplodingWriter:
        def log_event(self, event):
            nonlocal call_count
            call_count += 1
            raise RuntimeError("Audit writer exploded")

    # No session = allow path, but logging will throw
    monkeypatch.setattr(
        des_task_signal, "DES_DELIVER_SESSION_FILE", tmp_path / "nonexistent"
    )
    monkeypatch.setattr(
        des_task_signal, "DES_TASK_ACTIVE_FILE", tmp_path / "nonexistent"
    )

    monkeypatch.setattr("sys.stdin", io.StringIO(_build_pre_write_stdin("src/app.py")))
    printed = []
    monkeypatch.setattr("builtins.print", lambda *a, **kw: printed.append(a))

    with patch.object(
        hook_protocol, "_audit_writer_factory", return_value=ExplodingWriter()
    ):
        exit_code = adapter.handle_pre_write()

    # Must still allow (fail-open)
    assert exit_code == 0
    # Verify it attempted to log (writer was called)
    assert call_count > 0, "Expected audit writer to be called even though it raised"
    # Allow path: no stdout (Copilot protocol — silent exit 0)
    assert len(printed) == 0, f"Allow path should produce no output. Got: {printed}"


# --- Test 6: Execution log Write always blocked — guides to des.cli.init_log ---


def test_execution_log_write_blocked_always(monkeypatch, tmp_path):
    """Direct Write to execution-log.json is blocked and guides to des.cli.init_log."""
    from des.adapters.drivers.hooks import pre_write_handler as adapter

    events = []
    writer = make_capturing_writer(events)

    # No session active -- guard is unconditional
    monkeypatch.setattr(
        des_task_signal, "DES_DELIVER_SESSION_FILE", tmp_path / "nonexistent"
    )
    monkeypatch.setattr(
        des_task_signal, "DES_TASK_ACTIVE_FILE", tmp_path / "nonexistent"
    )

    exec_log_path = str(tmp_path / "project" / "execution-log.json")
    monkeypatch.setattr("sys.stdin", io.StringIO(_build_pre_write_stdin(exec_log_path)))
    printed = []
    monkeypatch.setattr("builtins.print", lambda *a, **kw: printed.append(a))

    with patch.object(hook_protocol, "_audit_writer_factory", return_value=writer):
        exit_code = adapter.handle_pre_write()

    # Must block
    assert exit_code == 0

    # Verify block response guides to init_log CLI
    assert len(printed) >= 1, "Expected at least one print call with block response"
    response_json = json.loads(printed[-1][0])
    hook_output = response_json["hookSpecificOutput"]
    assert hook_output["permissionDecision"] == "deny"
    assert "execution-log.json" in hook_output["permissionDecisionReason"]
    assert "des.cli.init_log" in hook_output["permissionDecisionReason"]

    # Verify audit event
    blocked_events = [e for e in events if e.event_type == "HOOK_PRE_WRITE_BLOCKED"]
    assert len(blocked_events) == 1, (
        f"Expected one HOOK_PRE_WRITE_BLOCKED event, got {len(blocked_events)}. "
        f"All events: {[e.event_type for e in events]}"
    )
    assert blocked_events[0].data["reason"] == "execution_log_direct_write"


# --- Test 7: Execution log Edit always blocked — guides to des.cli.log_phase ---


def test_execution_log_edit_blocked_always(monkeypatch, tmp_path):
    """Direct Edit to execution-log.json is blocked and guides to des.cli.log_phase."""
    from des.adapters.drivers.hooks import pre_write_handler as adapter

    events = []
    writer = make_capturing_writer(events)

    # No session active -- guard is unconditional
    monkeypatch.setattr(
        des_task_signal, "DES_DELIVER_SESSION_FILE", tmp_path / "nonexistent"
    )
    monkeypatch.setattr(
        des_task_signal, "DES_TASK_ACTIVE_FILE", tmp_path / "nonexistent"
    )

    exec_log_path = str(tmp_path / "feature" / "execution-log.json")
    monkeypatch.setattr("sys.stdin", io.StringIO(_build_pre_edit_stdin(exec_log_path)))
    printed = []
    monkeypatch.setattr("builtins.print", lambda *a, **kw: printed.append(a))

    with patch.object(hook_protocol, "_audit_writer_factory", return_value=writer):
        exit_code = adapter.handle_pre_write()

    # Must block
    assert exit_code == 0

    # Verify block response guides to log_phase CLI
    assert len(printed) >= 1, "Expected at least one print call with block response"
    response_json = json.loads(printed[-1][0])
    hook_output = response_json["hookSpecificOutput"]
    assert hook_output["permissionDecision"] == "deny"
    assert "execution-log.json" in hook_output["permissionDecisionReason"]
    assert "des.cli.log_phase" in hook_output["permissionDecisionReason"]

    # Verify audit event
    blocked_events = [e for e in events if e.event_type == "HOOK_PRE_WRITE_BLOCKED"]
    assert len(blocked_events) == 1, (
        f"Expected one HOOK_PRE_WRITE_BLOCKED event, got {len(blocked_events)}. "
        f"All events: {[e.event_type for e in events]}"
    )
    assert blocked_events[0].data["reason"] == "execution_log_direct_write"


# --- Test 8: Write vs Edit get different block messages ---


def test_create_file_and_replace_string_get_different_block_messages(monkeypatch, tmp_path):
    """create_file guides to des.cli.init_log, replace_string_in_file guides to des.cli.log_phase."""
    from des.adapters.drivers.hooks import pre_write_handler as adapter

    monkeypatch.setattr(
        des_task_signal, "DES_DELIVER_SESSION_FILE", tmp_path / "nonexistent"
    )
    monkeypatch.setattr(
        des_task_signal, "DES_TASK_ACTIVE_FILE", tmp_path / "nonexistent"
    )

    exec_log_path = str(tmp_path / "project" / "execution-log.json")

    # Collect create_file block message
    monkeypatch.setattr("sys.stdin", io.StringIO(_build_pre_write_stdin(exec_log_path)))
    create_printed = []
    monkeypatch.setattr("builtins.print", lambda *a, **kw: create_printed.append(a))

    writer = make_capturing_writer([])
    with patch.object(hook_protocol, "_audit_writer_factory", return_value=writer):
        adapter.handle_pre_write()

    create_reason = json.loads(create_printed[-1][0])["hookSpecificOutput"][
        "permissionDecisionReason"
    ]

    # Collect replace_string_in_file block message
    monkeypatch.setattr("sys.stdin", io.StringIO(_build_pre_edit_stdin(exec_log_path)))
    replace_printed = []
    monkeypatch.setattr("builtins.print", lambda *a, **kw: replace_printed.append(a))

    with patch.object(hook_protocol, "_audit_writer_factory", return_value=writer):
        adapter.handle_pre_write()

    replace_reason = json.loads(replace_printed[-1][0])["hookSpecificOutput"][
        "permissionDecisionReason"
    ]

    # Messages must differ and guide to different CLIs
    assert create_reason != replace_reason, (
        "create_file and replace_string_in_file should get different block messages"
    )
    assert "init_log" in create_reason
    assert "log_phase" in replace_reason
    assert "init_log" not in replace_reason
    assert "log_phase" not in create_reason


# --- Test 9: Early-return for non-write tools (early optimization) ---


def test_early_return_for_non_write_tools(monkeypatch, tmp_path):
    """Early-return exit 0 (no output) when tool_name not in COPILOT_WRITE_TOOLS."""
    from des.adapters.drivers.hooks import pre_write_handler as adapter

    events = []
    writer = make_capturing_writer(events)

    # No session, no DES task
    monkeypatch.setattr(
        des_task_signal, "DES_DELIVER_SESSION_FILE", tmp_path / "nonexistent"
    )
    monkeypatch.setattr(
        des_task_signal, "DES_TASK_ACTIVE_FILE", tmp_path / "nonexistent"
    )

    # Tool name is "read_file" (not a write tool)
    stdin_json = json.dumps({
        "tool_name": "read_file",
        "tool_input": {"filePath": "src/main.py"}
    })
    monkeypatch.setattr("sys.stdin", io.StringIO(stdin_json))
    printed = []
    monkeypatch.setattr("builtins.print", lambda *a, **kw: printed.append(a))

    with patch.object(hook_protocol, "_audit_writer_factory", return_value=writer):
        exit_code = adapter.handle_pre_write()

    # Must exit 0 (silent allow, no output)
    assert exit_code == 0
    # No stdout output (early return optimization)
    assert len(printed) == 0, (
        f"Early-return for non-write tool should produce no output. Got: {printed}"
    )
    # No pre-write-specific audit events (early return skips all logic)
    # Note: HOOK_COMPLETED is still emitted as part of normal hook completion
    specific_events = [e for e in events if e.event_type.startswith("HOOK_PRE_WRITE")]
    assert len(specific_events) == 0, (
        f"Early-return should not produce HOOK_PRE_WRITE events. Got: {[e.event_type for e in events]}"
    )
