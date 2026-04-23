"""
CopilotTaskAdapter - production task invocation implementation.

Provides integration with GitHub Copilot's task invocation mechanism
for invoking sub-agents in production environments.
"""

from typing import Any

from des.ports.driven_ports.task_invocation_port import TaskInvocationPort


class CopilotTaskAdapter(TaskInvocationPort):
    """
    Production task invocation adapter for GitHub Copilot.

    This adapter integrates with GitHub Copilot's sub-agent invocation
    mechanism to invoke sub-agents and return their results.
    """

    def invoke_task(self, prompt: str, agent: str) -> dict[str, Any]:
        """
        Invoke a sub-agent task using GitHub Copilot's task mechanism.

        Args:
            prompt: The prompt to send to the sub-agent
            agent: The agent identifier to invoke

        Returns:
            Task result dictionary with keys:
            - success: bool
            - output: str (if successful)
            - error: str (if failed)

        Raises:
            NotImplementedError: Production task invocation integration pending.
                                Use MockedTaskAdapter for testing.

        Note:
            This adapter is a placeholder for future GitHub Copilot task
            invocation integration. Current implementation intentionally raises
            NotImplementedError to prevent accidental use in production before
            integration is complete.
        """
        raise NotImplementedError(
            "CopilotTaskAdapter requires integration with actual Copilot task mechanism. "
            "Use MockedTaskAdapter for testing."
        )
