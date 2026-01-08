# Changelog

All notable changes to ragctl will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.5] - 2026-01-08

### Added
- Dry-run mode for batch command to preview files before processing
- Global quiet and verbose flags for better control over output
- Support for `-q/--quiet` flag to suppress non-error messages
- Support for `-v/--verbose` and `-vv` flags for debug output
- Tests for verbosity flags functionality
- Improved documentation with examples for dry-run and verbosity features

### Changed
- Version flag changed from `-v` to `-V` to avoid conflict with verbose flag

### Contributors
- @SoulSniper-V2 - Dry-run implementation
- @cnaples79 - Verbosity flags implementation

## [0.1.4] - 2026-01-05

### Changed
- Updated repository URLs from ragstudio to ragctl
- Improved documentation and examples

## [0.1.3] - 2025-10-30

### ✅ Testing & Quality Improvements

**Test Coverage Expansion** - 37% → 41%:
- Added 60 comprehensive tests for security utilities
- security.py coverage: 0% → 89%
- Total unit tests: 436 → 496 (+60 tests)
- All 496 tests passing (100% success rate)

**New Test Modules**:
- test_security.py (60 tests) - Comprehensive security validation tests
  - SecurityConfig and environment loading
  - Path security (path traversal, symlinks, pattern validation)
  - File size validation (individual and batch)
  - Disk space validation
  - MIME type validation
  - Metadata sanitization

**Database Migration**:
- Completed PostgreSQL → SQLite migration
- Removed all PostgreSQL-specific code (JSONB → JSON)
- metadata_store.py: 17% → 89% coverage

### 🧹 Code Quality

**Git History Cleanup**:
- Removed .archive directory from git tracking
- Clean commit history for production release

## [0.1.2] - 2025-10-29

### 🎨 Rebranding

**ragctl** - Professional rebrand with improved naming:
- **Project name**: Atlas-RAG → **ragctl**
- **Package name**: atlas-rag → **ragctl** (follows kubectl/systemctl convention)
- **CLI command**: `atlas-rag` → `ragctl`
- **Repository**: horiz-data/ragstudio → datallmhub/ragctl

### ⚡ Performance Improvements

**CLI Startup Optimization** - 100x faster:
- Implemented lazy imports for heavy modules (torch, transformers, langchain)
- Startup time: 5-10s → 0.08s
- `ragctl --version` now instant
- Commands load dependencies only when needed

### ✨ New Features

**User Experience**:
- Suppressed transformers FutureWarning for cleaner output
- Updated all help text and branding to RAG Studio
- Improved version display format
