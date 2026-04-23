#!/usr/bin/env python3
"""GitHub Copilot hook adapter — entry point for DES hooks.

Thin facade: parses argv command, delegates to the appropriate handler.
Each handler reads stdin and emits hookSpecificOutput natively.

Usage:
    python -m des.adapters.drivers.hooks.copilot_hook_adapter <command>

Commands: pre-tool-use, post-tool-use, session-start, subagent-start,
          subagent-stop, deliver-progress
"""

from __future__ import annotations

import json
import sys
import io
import contextlib

def extract_des_context_from_transcript(transcript_path: str) -> dict | None:
    from des.adapters.drivers.hooks.subagent_stop_handler import (
        extract_des_context_from_transcript as _extract,
    )

    return _extract(transcript_path)


def _run_handler_with_capture(handler_func):
    """Run a handler while capturing its stdout.

    Returns (captured_stdout_str, exit_code).
    """
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exit_code = handler_func()
    return buf.getvalue(), exit_code


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: copilot_hook_adapter <command>"}), file=sys.stderr)
        sys.exit(2)

    command = sys.argv[1]

    if command == "pre-tool-use":
        from des.adapters.drivers.hooks.pre_tool_use_handler import handle_pre_tool_use

        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            exit_code = handle_pre_tool_use()

        handler_stdout = captured.getvalue().strip()

        if exit_code == 0:
            # Allow (silent) or block (hookSpecificOutput JSON on stdout)
            if handler_stdout:
                print(handler_stdout)
            sys.exit(0)
        else:
            # Error path: Copilot expects details on stderr.
            if handler_stdout:
                print(handler_stdout, file=sys.stderr)
            else:
                print("DES PreToolUse error", file=sys.stderr)
            sys.exit(2)

    elif command == "post-tool-use":
        from des.adapters.drivers.hooks.post_tool_use_handler import handle_post_tool_use
        exit_code = handle_post_tool_use()
        sys.exit(exit_code)

    elif command == "session-start":
        from des.adapters.drivers.hooks.session_start_handler import handle_session_start
        exit_code = handle_session_start()
        sys.exit(exit_code)

    elif command == "subagent-start":
        from des.adapters.drivers.hooks.copilot_subagent_start_handler import handle_subagent_start_copilot
        exit_code = handle_subagent_start_copilot()
        sys.exit(exit_code)

    elif command in ("pre-write", "pre-edit"):
        from des.adapters.drivers.hooks.pre_write_handler import handle_pre_write

        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            exit_code = handle_pre_write()

        handler_stdout = captured.getvalue().strip()

        if exit_code == 0:
            # Allow (silent) or block (hookSpecificOutput JSON on stdout)
            if handler_stdout:
                print(handler_stdout)
            sys.exit(0)
        else:
            if handler_stdout:
                print(handler_stdout, file=sys.stderr)
            else:
                print("DES PreWrite error", file=sys.stderr)
            sys.exit(2)

    elif command == "subagent-stop":
        from des.adapters.drivers.hooks.subagent_stop_handler import handle_subagent_stop
        exit_code = handle_subagent_stop()
        sys.exit(exit_code)

    elif command == "deliver-progress":
        from des.adapters.drivers.hooks.deliver_progress_handler import handle_deliver_progress
        exit_code = handle_deliver_progress()
        sys.exit(exit_code)

    else:
        print(f"DES: Unknown command: {command}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()

