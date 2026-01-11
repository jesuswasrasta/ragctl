"""Tests for the eval command."""
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.core.cli.app import app

class TestEvalCommand:
    """Test cases for ragctl eval command."""

    @pytest.fixture
    def source_file(self, tmp_path):
        """Create a temporary source file."""
        file_path = tmp_path / "doc.txt"
        file_path.write_text("Test document content.")
        return file_path

    @patch("src.core.cli.commands.chunk.chunk_command")
    def test_eval_basic(self, mock_chunk, mock_cli_runner, source_file):
        """Test basic evaluation."""
        # Mock chunk_command to write dummy chunks
        def side_effect(**kwargs):
            output = kwargs.get("output")
            if output:
                data = [
                    {"text": "Chunk 1", "metadata": {}},
                    {"text": "Chunk 2", "metadata": {}}
                ]
                with open(output, "w") as f:
                    json.dump(data, f)
            return 0
        
        mock_chunk.side_effect = side_effect

        result = mock_cli_runner.invoke(app, ["eval", str(source_file), "--strategies", "semantic"])

        assert result.exit_code == 0
        assert "Evaluating chunking quality" in result.stdout
        assert "Chunk 1" not in result.stdout # Details not shown by default
        assert "Total chunks" in result.stdout

    @patch("src.core.cli.commands.chunk.chunk_command")
    def test_eval_compare(self, mock_chunk, mock_cli_runner, source_file):
        """Test evaluation with comparison."""
        def side_effect(**kwargs):
            output = kwargs.get("output")
            strategy = kwargs.get("strategy")
            if output:
                # Vary content based on strategy
                if strategy == "semantic":
                    data = [{"text": "Sem 1"}, {"text": "Sem 2"}]
                else:
                    data = [{"text": "Sen 1"}, {"text": "Sen 2"}, {"text": "Sen 3"}]
                
                with open(output, "w") as f:
                    json.dump(data, f)
            return 0
            
        mock_chunk.side_effect = side_effect

        result = mock_cli_runner.invoke(app, ["eval", str(source_file), "--strategies", "semantic,sentence"])

        assert result.exit_code == 0
        assert "Comparison" in result.stdout
        assert "semantic" in result.stdout
        assert "sentence" in result.stdout

    @patch("src.core.cli.commands.chunk.chunk_command")
    def test_eval_chunk_failure(self, mock_chunk, mock_cli_runner, source_file):
        """Test eval when chunking fails."""
        mock_chunk.return_value = 1 # Failure

        result = mock_cli_runner.invoke(app, ["eval", str(source_file)])

        # If all chunking fails, it should exit with error or warning
        # app.py: if not temp_files: ... return 0 but prints warning
        assert result.exit_code == 0
        assert "Cannot evaluate empty file" in result.stdout
