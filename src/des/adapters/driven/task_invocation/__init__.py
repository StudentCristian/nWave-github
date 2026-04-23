"""Task invocation driven adapters."""

from des.adapters.driven.task_invocation.copilot_task_adapter import (
    CopilotTaskAdapter,
)
from des.adapters.driven.task_invocation.mocked_task_adapter import (
    MockedTaskAdapter,
)


__all__ = ["CopilotTaskAdapter", "MockedTaskAdapter"]
