"""Tests for the retry command."""
import pytest
from unittest.mock import patch, MagicMock
from src.core.cli.app import app
from src.core.pipeline import FileStatus

class TestRetryCommand:
    """Test cases for ragctl retry command."""

    @pytest.fixture
    def mock_history(self):
        with patch("src.core.cli.commands.retry.HistoryManager") as mock:
            yield mock

    @pytest.fixture
    def mock_chunk(self):
        with patch("src.core.chunk.chunker.chunk_document") as mock:
            yield mock

    def test_retry_no_run_id_no_failed(self, mock_history, mock_cli_runner):
        """Test retry with no run ID and no failed runs in history."""
        manager = mock_history.return_value
        manager.get_last_failed_run.return_value = None

        result = mock_cli_runner.invoke(app, ["retry"])

        assert result.exit_code == 1
        assert "No failed runs found" in result.stdout

    def test_retry_specific_run_not_found(self, mock_history, mock_cli_runner):
        """Test retry with non-existent run ID."""
        manager = mock_history.return_value
        manager.get_run.return_value = None

        result = mock_cli_runner.invoke(app, ["retry", "run_123"])

        assert result.exit_code == 1
        assert "Run not found" in result.stdout

    def test_retry_success(self, mock_history, mock_chunk, mock_cli_runner, tmp_path):
        """Test successful retry of a failed run."""
        manager = mock_history.return_value
        
        # Mock run
        mock_run = MagicMock()
        mock_run.run_id = "run_123"
        mock_run.config = {}
        manager.get_last_failed_run.return_value = mock_run
        manager.get_run.return_value = mock_run

        # Mock failed files
        # We need objects with .filepath, .filename, .status attributes
        class MockFileResult:
            def __init__(self, path):
                self.filepath = str(path)
                self.filename = path.name
                self.status = FileStatus.FAILED
                self.error = "Mock error"
                self.reason = None
                self.retries = 0
        
        doc_path = tmp_path / "doc.txt"
        doc_path.write_text("content")
        
        failed_file = MockFileResult(doc_path)
        manager.get_failed_files.return_value = [failed_file]
        
        # Mock create_run and start_run
        mock_retry_run = MagicMock()
        mock_retry_run.run_id = "retry_run_456"
        mock_retry_run.success = 1
        mock_retry_run.failed = 0
        mock_retry_run.skipped = 0
        mock_retry_run.aborted = 0
        
        manager.create_run.return_value = mock_retry_run

        # Mock chunking success
        mock_chunk.return_value = {"chunks": [1, 2]}

        # Run with --yes (via input or confirm mock, but typer confirm prompts on stderr)
        # We can use 'input' argument to invoke
        result = mock_cli_runner.invoke(app, ["retry", "run_123"], input="y\n")

        assert result.exit_code == 0
        assert "Starting retry" in result.stdout
        assert "Processing: doc.txt" in result.stdout
        assert "Success:" in result.stdout and "1/1" in result.stdout

    def test_retry_show(self, mock_history, mock_cli_runner, tmp_path):
        """Test retry --show (dry run)."""
        manager = mock_history.return_value
        
        mock_run = MagicMock()
        mock_run.run_id = "run_123"
        manager.get_last_failed_run.return_value = mock_run
        
        class MockFileResult:
            def __init__(self, path):
                self.filepath = str(path)
                self.filename = path.name
                self.status = FileStatus.FAILED
                self.error = "Mock error"
                self.reason = None
                self.retries = 0

        doc_path = tmp_path / "doc.txt"
        failed_file = MockFileResult(doc_path)
        manager.get_failed_files.return_value = [failed_file]

        result = mock_cli_runner.invoke(app, ["retry", "--show"])

        assert result.exit_code == 0
        assert "Found 1 file(s) to retry" in result.stdout
        assert "Dry run mode" in result.stdout
