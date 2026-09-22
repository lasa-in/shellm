"""Integration test for the agent tool loop — LLM is mocked, no API key needed."""

import json
import pytest
from unittest.mock import patch, MagicMock

from shellm.agent import run_agent


def make_tool_call(name: str, args: dict, call_id: str = "call_1"):
    """Build a mock tool_call object."""
    tc = MagicMock()
    tc.id = call_id
    tc.function.name = name
    tc.function.arguments = json.dumps(args)
    return tc


def make_llm_response(content=None, tool_calls=None):
    """Build a mock LiteLLM completion response."""
    response = MagicMock()
    message = MagicMock()
    message.content = content
    message.tool_calls = tool_calls or []
    response.choices = [MagicMock(message=message)]
    return response


class TestAgentLoop:
    def test_direct_answer_no_tools(self):
        """Agent returns a direct text answer when no tools are needed."""
        with patch("shellm.agent.litellm.completion") as mock_llm:
            mock_llm.return_value = make_llm_response(content="Hello! I'm shellm.")

            response, history = run_agent("say hello", "gpt-4o", [])

        assert response == "Hello! I'm shellm."
        assert history[-1]["role"] == "assistant"
        assert history[-1]["content"] == "Hello! I'm shellm."

    def test_single_tool_call_bash(self):
        """Agent calls bash tool once then returns final answer."""
        bash_call = make_tool_call("bash", {"command": "echo hello"})

        with patch("shellm.agent.litellm.completion") as mock_llm:
            # First call → tool use; second call → final answer
            mock_llm.side_effect = [
                make_llm_response(tool_calls=[bash_call]),
                make_llm_response(content="The output is: hello"),
            ]

            response, history = run_agent("run echo hello", "gpt-4o", [])

        assert response == "The output is: hello"
        assert mock_llm.call_count == 2

    def test_multi_step_tool_chain(self):
        """Agent chains two tool calls before returning a final answer."""
        write_call = make_tool_call("write_file", {"path": "/tmp/x.txt", "content": "hi"}, "call_1")
        read_call  = make_tool_call("read_file",  {"path": "/tmp/x.txt"}, "call_2")

        with patch("shellm.agent.litellm.completion") as mock_llm:
            mock_llm.side_effect = [
                make_llm_response(tool_calls=[write_call]),
                make_llm_response(tool_calls=[read_call]),
                make_llm_response(content="Done — file written and read back successfully."),
            ]

            response, history = run_agent("write then read /tmp/x.txt", "gpt-4o", [])

        assert "Done" in response
        assert mock_llm.call_count == 3

    def test_unknown_tool_returns_error(self):
        """Agent handles unknown tool names gracefully."""
        unknown_call = make_tool_call("nonexistent_tool", {}, "call_x")

        with patch("shellm.agent.litellm.completion") as mock_llm:
            mock_llm.side_effect = [
                make_llm_response(tool_calls=[unknown_call]),
                make_llm_response(content="I couldn't find that tool."),
            ]

            response, history = run_agent("use unknown tool", "gpt-4o", [])

        # Should not crash — second LLM call gets error message as tool result
        assert mock_llm.call_count == 2

    def test_conversation_history_maintained(self):
        """History grows correctly across multiple turns."""
        with patch("shellm.agent.litellm.completion") as mock_llm:
            mock_llm.return_value = make_llm_response(content="Turn 1 answer.")
            _, history = run_agent("first question", "gpt-4o", [])

        assert len(history) == 2  # user + assistant
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"
