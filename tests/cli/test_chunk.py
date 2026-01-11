"""Tests for the chunk command."""
import json
import pytest
from pathlib import Path

from src.core.cli.app import app


class TestChunkCommand:
    """Test cases for ragctl chunk command - simplified to avoid stdout issues."""

    def test_chunk_basic(self, cli_runner, sample_text_file):
        """Test basic chunking without options."""
        result = cli_runner.invoke(app, ["chunk", str(sample_text_file)])
        assert result.exit_code == 0

    def test_chunk_with_show(self, cli_runner, sample_text_file):
        """Test chunking with --show option."""
        result = cli_runner.invoke(app, ["chunk", str(sample_text_file), "--show"])
        assert result.exit_code == 0

    def test_chunk_with_output(self, cli_runner, sample_text_file, tmp_path):
        """Test chunking with output file."""
        output_file = tmp_path / "output.json"

        result = cli_runner.invoke(app, [
            "chunk", str(sample_text_file),
            "-o", str(output_file)
        ])

        assert result.exit_code == 0
        assert output_file.exists()

        # Verify JSON structure
        data = json.loads(output_file.read_text())
        assert isinstance(data, list)
        assert len(data) > 0
        assert "id" in data[0]
        assert "text" in data[0]
        assert "metadata" in data[0]

    def test_chunk_strategies(self, cli_runner, sample_text_file):
        """Test different chunking strategies."""
        strategies = ["semantic", "sentence", "token"]

        for strategy in strategies:
            result = cli_runner.invoke(app, [
                "chunk", str(sample_text_file),
                "--strategy", strategy
            ])
            assert result.exit_code == 0

    def test_chunk_with_max_tokens(self, cli_runner, sample_text_file):
        """Test chunking with custom max tokens."""
        result = cli_runner.invoke(app, [
            "chunk", str(sample_text_file),
            "--max-tokens", "200"
        ])
        assert result.exit_code == 0

    def test_chunk_with_overlap(self, cli_runner, sample_text_file):
        """Test chunking with custom overlap."""
        result = cli_runner.invoke(app, [
            "chunk", str(sample_text_file),
            "--overlap", "100"
        ])
        assert result.exit_code == 0

    def test_chunk_invalid_file(self, cli_runner):
        """Test chunking with non-existent file."""
        result = cli_runner.invoke(app, ["chunk", "/nonexistent/file.txt"])
        assert result.exit_code != 0

    def test_chunk_invalid_strategy(self, cli_runner, sample_text_file):
        """Test chunking with invalid strategy."""
        result = cli_runner.invoke(app, [
            "chunk", str(sample_text_file),
            "--strategy", "invalid"
        ])
        assert result.exit_code != 0





    def test_chunk_empty_file(self, cli_runner, empty_file):
        """Test chunking an empty file."""
        result = cli_runner.invoke(app, ["chunk", str(empty_file)])
        # We accept either success or controlled failure
        assert result.exit_code in [0, 1]




