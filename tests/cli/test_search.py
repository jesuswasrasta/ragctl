"""Tests for the search command."""
import json
import pytest
from unittest.mock import patch, MagicMock
from src.core.cli.app import app

class TestSearchCommand:
    """Test cases for ragctl search command."""

    @patch("src.core.vector.QdrantVectorStore")
    def test_search_basic(self, MockQdrant, mock_cli_runner):
        """Test basic search."""
        mock_store = MockQdrant.return_value
        mock_store.search_by_text.return_value = [
            {
                "id": "1",
                "score": 0.95,
                "text": "Result text",
                "metadata": {"source": "doc1.txt"}
            }
        ]

        result = mock_cli_runner.invoke(app, ["search", "query"])

        assert result.exit_code == 0
        assert "Found 1 results" in result.stdout
        assert "Result text" in result.stdout

    @patch("src.core.vector.QdrantVectorStore")
    def test_search_json_output(self, MockQdrant, mock_cli_runner):
        """Test search with JSON output."""
        mock_store = MockQdrant.return_value
        mock_store.search_by_text.return_value = [
            {
                "id": "1",
                "score": 0.95,
                "text": "Result text",
                "metadata": {"source": "doc1.txt"}
            }
        ]

        result = mock_cli_runner.invoke(app, ["search", "query", "--json-output"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["results_count"] == 1
        assert data["results"][0]["id"] == "1"

    @patch("src.core.vector.QdrantVectorStore")
    def test_search_no_results(self, MockQdrant, mock_cli_runner):
        """Test search with no results."""
        mock_store = MockQdrant.return_value
        mock_store.search_by_text.return_value = []

        result = mock_cli_runner.invoke(app, ["search", "query"])

        assert result.exit_code == 0
        assert "Found 0 results" in result.stdout
        assert "No results found" in result.stdout

    @patch("src.core.vector.QdrantVectorStore")
    def test_search_connection_error(self, MockQdrant, mock_cli_runner):
        """Test search when connection fails."""
        mock_store = MockQdrant.return_value
        mock_store.connect.side_effect = Exception("Connection refused")

        result = mock_cli_runner.invoke(app, ["search", "query"])

        assert result.exit_code == 1
        assert "Failed to connect" in result.stdout
