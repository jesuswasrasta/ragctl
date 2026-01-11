"""Unit tests for search command."""
import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from click.exceptions import Exit as ClickExit
import typer

from src.core.cli.commands.search import search_command


class TestSearchCommand:
    """Tests for search command using direct VectorStore."""

    @patch('src.core.cli.commands.search.QdrantVectorStore')
    def test_search_successful(self, mock_store_class):
        """Test successful search operation."""
        # Mock vector store
        mock_store = Mock()
        mock_store_class.return_value = mock_store
        
        # Mock search results
        mock_store.search_by_text.return_value = [
            {
                "id": "chunk_1",
                "score": 0.85,
                "text": "Machine learning is a subset of AI",
                "metadata": {"source_file": "ml_intro.pdf", "page_number": 5}
            }
        ]

        # Execute search
        search_command(query="machine learning", collection="test_coll")

        # Verify calls
        mock_store.connect.assert_called_once()
        mock_store.search_by_text.assert_called_once_with(
            query="machine learning",
            top_k=5,
            score_threshold=None
        )

    @patch('src.core.cli.commands.search.QdrantVectorStore')
    def test_search_with_parameters(self, mock_store_class):
        """Test search with custom parameters."""
        mock_store = Mock()
        mock_store_class.return_value = mock_store
        mock_store.search_by_text.return_value = []

        # Execute search with custom params
        search_command(
            query="test query",
            top_k=10,
            threshold=0.7,
            collection="custom_coll"
        )

        # Verify params passed correctly
        mock_store.search_by_text.assert_called_once_with(
            query="test query",
            top_k=10,
            score_threshold=0.7
        )

    @patch('src.core.cli.commands.search.QdrantVectorStore')
    def test_search_json_output(self, mock_store_class, capsys):
        """Test search with JSON output."""
        mock_store = Mock()
        mock_store_class.return_value = mock_store
        
        mock_results = [
            {
                "id": "c1",
                "score": 0.9,
                "text": "test",
                "metadata": {}
            }
        ]
        mock_store.search_by_text.return_value = mock_results

        # Execute with --json-output
        search_command(query="test", json_output=True)

        # Check stdout for JSON
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        
        assert output["query"] == "test"
        assert output["results_count"] == 1
        assert output["results"][0]["id"] == "c1"

    @patch('src.core.cli.commands.search.QdrantVectorStore')
    def test_search_connection_error(self, mock_store_class):
        """Test handling of connection errors."""
        mock_store = Mock()
        mock_store_class.return_value = mock_store
        mock_store.connect.side_effect = Exception("Connection refused")

        # Verify Exit is raised
        with pytest.raises((ClickExit, typer.Exit)):
            search_command(query="test")

    @patch('src.core.cli.commands.search.QdrantVectorStore')
    def test_search_execution_error(self, mock_store_class):
        """Test handling of search errors."""
        mock_store = Mock()
        mock_store_class.return_value = mock_store
        mock_store.search_by_text.side_effect = Exception("Search failed")

        # Verify Exit is raised
        with pytest.raises((ClickExit, typer.Exit)):
            search_command(query="test")

