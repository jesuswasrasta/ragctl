"""Tests for the info command."""
import pytest
from unittest.mock import patch, MagicMock
from src.core.cli.app import app

class TestInfoCommand:
    """Test cases for ragctl info command."""

    @patch("requests.get")
    def test_info_basic(self, mock_get, mock_cli_runner):
        """Test basic info command with available API."""
        # Mock API health check
        mock_health = MagicMock()
        mock_health.json.return_value = {"status": "ok", "version": "0.1.0"}
        
        # Mock Vector Store info
        mock_vector = MagicMock()
        mock_vector.json.return_value = {
            "name": "atlas_chunks",
            "vectors_count": 100,
            "config": {"dimension": 384}
        }
        
        mock_get.side_effect = [mock_health, mock_vector]

        result = mock_cli_runner.invoke(app, ["info"])

        assert result.exit_code == 0
        assert "RAG Studio System Information" in result.stdout
        assert "API Status: ok" in result.stdout
        assert "Vector Store: Connected" in result.stdout
        assert "Vectors: 100" in result.stdout

    @patch("requests.get")
    def test_info_api_unavailable(self, mock_get, mock_cli_runner):
        """Test info command when API is unavailable."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        result = mock_cli_runner.invoke(app, ["info"])

        assert result.exit_code == 0
        assert "API: Not available" in result.stdout
        assert "Local Capabilities" in result.stdout

    @patch("requests.get")
    def test_info_vector_store_error(self, mock_get, mock_cli_runner):
        """Test info command when Vector Store check fails."""
        # API OK
        mock_health = MagicMock()
        mock_health.json.return_value = {"status": "ok", "version": "0.1.0"}
        
        # Vector Store Error
        mock_get.side_effect = [mock_health, Exception("Vector DB Error")]

        result = mock_cli_runner.invoke(app, ["info"])

        assert result.exit_code == 0
        assert "API Status: ok" in result.stdout
        assert "Vector Store: Not initialized or error" in result.stdout
