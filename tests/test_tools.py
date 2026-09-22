"""Unit tests for shellm tools — no LLM or API key required."""

import os
import tempfile
import pytest

from shellm.tools.bash import run_bash
from shellm.tools.files import read_file, write_file, list_dir


# ── bash tool ────────────────────────────────────────────────────────────────

class TestBash:
    def test_simple_command(self):
        result = run_bash("echo hello")
        assert result == "hello"

    def test_multiline_output(self):
        result = run_bash("printf 'line1\nline2\nline3'")
        assert "line1" in result
        assert "line3" in result

    def test_stderr_captured(self):
        result = run_bash("echo error >&2")
        assert "error" in result

    def test_nonzero_exit_code(self):
        result = run_bash("exit 1")
        assert "exit code: 1" in result

    def test_timeout(self):
        result = run_bash("sleep 10", timeout=1)
        assert "timed out" in result

    def test_invalid_command(self):
        result = run_bash("thiscommanddoesnotexist_xyz")
        assert result  # returns something, not empty


# ── file tools ───────────────────────────────────────────────────────────────

class TestFiles:
    def test_write_and_read(self, tmp_path):
        path = str(tmp_path / "test.txt")
        write_result = write_file(path, "hello shellm")
        assert "Written" in write_result

        read_result = read_file(path)
        assert read_result == "hello shellm"

    def test_read_missing_file(self):
        result = read_file("/tmp/does_not_exist_xyz_shellm.txt")
        assert "error" in result.lower()

    def test_write_creates_directories(self, tmp_path):
        path = str(tmp_path / "nested" / "dir" / "file.txt")
        result = write_file(path, "nested content")
        assert "Written" in result
        assert os.path.exists(path)

    def test_list_dir(self, tmp_path):
        (tmp_path / "file_a.py").write_text("a")
        (tmp_path / "file_b.txt").write_text("b")
        (tmp_path / "subdir").mkdir()

        result = list_dir(str(tmp_path))
        assert "file_a.py" in result
        assert "file_b.txt" in result
        assert "subdir" in result

    def test_list_dir_missing(self):
        result = list_dir("/tmp/does_not_exist_xyz_shellm")
        assert "error" in result.lower()

    def test_list_empty_dir(self, tmp_path):
        result = list_dir(str(tmp_path))
        assert "empty" in result.lower()
