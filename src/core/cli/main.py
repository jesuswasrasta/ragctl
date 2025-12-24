#!/usr/bin/env python3
"""
ragctl CLI - Main Entry Point

This module provides the main entry point for the ragctl CLI.
The CLI has been migrated to Typer for better UX and maintainability.
"""

from src.core.cli.app import app


def main():
    """Main entry point for ragctl CLI."""
    app()


if __name__ == '__main__':
    main()
