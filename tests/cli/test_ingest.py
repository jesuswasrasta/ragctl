"""Tests for the ingest command."""
import json
import pytest
from unittest.mock import patch, MagicMock
from src.core.cli.app import app

class TestIngestCommand:
    """Test cases for ragctl ingest command."""

    @pytest.fixture
    def chunks_file(self, tmp_path):
        """Create a temporary chunks file."""
        file_path = tmp_path / "chunks.json"
        data = [
            {
                "id": "1",
                "text": "Chunk 1",
                "metadata": {"source": "doc1.txt"}
            },
            {
                "id": "2",
                "text": "Chunk 2",
                "metadata": {"source": "doc1.txt"}
            }
        ]
        file_path.write_text(json.dumps(data))
        return file_path

    @patch("src.core.vector.QdrantVectorStore")
    def test_ingest_basic(self, MockQdrant, mock_cli_runner, chunks_file):
        """Test basic ingestion."""
        # Setup mock
        mock_store = MockQdrant.return_value
        mock_store.store_chunks.return_value = 2
        mock_store.index_exists.return_value = False

        result = mock_cli_runner.invoke(app, ["ingest", str(chunks_file)])

        assert result.exit_code == 0
        assert "Loading chunks" in result.stdout
        assert "Connected to Qdrant" in result.stdout
        assert "Ingestion complete" in result.stdout
        
        # Verify calls
        mock_store.connect.assert_called_once()
        mock_store.create_collection.assert_called_once()
        mock_store.store_chunks.assert_called()

    @patch("src.core.vector.QdrantVectorStore")
    def test_ingest_recreate(self, MockQdrant, mock_cli_runner, chunks_file):
        """Test ingestion with --recreate."""
        mock_store = MockQdrant.return_value
        mock_store.store_chunks.return_value = 2

        result = mock_cli_runner.invoke(app, ["ingest", str(chunks_file), "--recreate", "--yes"])

        assert result.exit_code == 0
        mock_store.create_collection.assert_called_with(recreate=True)

    def test_ingest_missing_file(self, mock_cli_runner):
        """Test ingestion with missing file."""
        result = mock_cli_runner.invoke(app, ["ingest", "nonexistent.json"])
        assert result.exit_code != 0
        # Typer/Click standard output for bad parameter
        assert "Cannot access file" in result.stdout or "does not exist" in result.stdout

    @patch("src.core.vector.QdrantVectorStore")
    def test_ingest_connection_error(self, MockQdrant, mock_cli_runner, chunks_file):
        """Test ingestion when connection fails."""
        mock_store = MockQdrant.return_value
        mock_store.connect.side_effect = Exception("Connection refused")

        result = mock_cli_runner.invoke(app, ["ingest", str(chunks_file)])

        assert result.exit_code == 1
        assert "Failed to connect" in result.stdout
