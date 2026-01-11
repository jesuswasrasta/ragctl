# ragctl

## Project Overview

**ragctl** is a production-ready command-line tool designed for processing documents into chunks suitable for Retrieval-Augmented Generation (RAG) systems. It acts as a comprehensive pipeline that handles document ingestion, Optical Character Recognition (OCR), semantic chunking, and vector store integration.

### Key Technologies
*   **Language:** Python 3.10+
*   **CLI Framework:** Typer, Rich
*   **Document Processing:** LangChain, Unstructured, PyMuPDF, PDFPlumber
*   **OCR Engines:** EasyOCR (primary), PaddleOCR, Tesseract, Qwen-VL (advanced)
*   **Vector Store:** Qdrant
*   **Build/Dependency Management:** Poetry (dev), Setuptools (packaging)

## Architecture

The system is designed around an **Intelligent Document Orchestrator** that routes documents to the most appropriate processing pipeline:

1.  **Ingestion:**
    *   **Text-based PDFs:** Processed via `PyMuPDF` (fast).
    *   **Scanned PDFs/Images:** Processed via `EasyOCR` or `PaddleOCR`.
    *   **Hybrid PDFs:** Analyzed to determine if text extraction is sufficient; falls back to OCR if needed.
2.  **OCR Cascade:**
    *   Advanced (Qwen-VL) -> Classic (EasyOCR) -> Fallback (PaddleOCR/Tesseract).
3.  **Chunking:**
    *   Strategies: `semantic` (LangChain RecursiveCharacterTextSplitter), `sentence`, `token`.
4.  **Output:**
    *   Exports to JSON, JSONL, CSV.
    *   Direct ingestion to Qdrant.

## Getting Started

### Prerequisites
*   Python 3.10+
*   System dependencies: `tesseract-ocr`, `poppler-utils` (for PDF processing)

### Installation (Development)

The project uses `poetry` for development dependency management and `make` for task automation.

```bash
# Install development dependencies
make install-dev

# Install pre-commit hooks
make pre-commit-install
```

### Running the CLI

You can run the CLI via `poetry` or directly if installed in the environment.

```bash
# Check version
ragctl --version

# Process a single file
ragctl chunk document.pdf --show

# Batch process a directory
ragctl batch ./documents --output ./chunks/
```

## Configuration

Configuration is managed hierarchically:
1.  **CLI Flags** (Highest priority)
2.  **Environment Variables** (e.g., `ATLAS_USE_LLM`)
3.  **Config File** (`~/.ragctl/config.yml`)
4.  **Defaults**

### Key Configuration Sections (`config.yml`)

*   **`llm`**: Settings for LLM providers (Ollama, OpenAI, Anthropic) used for text correction/analysis.
*   **`ocr`**:
    *   `use_advanced_ocr`: Toggles Qwen-VL usage.
    *   `dictionary_threshold`: Heuristic to decide when to switch between fast and advanced OCR.
*   **`chunking`**:
    *   `strategy`: `semantic`, `sentence`, or `token`.
    *   `max_tokens`: Context window size for chunks.
*   **`output`**: Format selection (JSON/JSONL/CSV) and metadata toggle.

## Development Workflow

### Common Commands (`Makefile`)

*   **`make test`**: Run all tests with coverage.
*   **`make test-cli`**: Run CLI-specific tests.
*   **`make lint`**: Run `ruff` and `mypy`.
*   **`make format`**: Format code with `black` and `isort`.
*   **`make ci-all`**: Run full CI suite (lint, test, security checks).

### Directory Structure

*   `src/core/cli`: CLI entry point (`main.py`) and command definitions.
*   `src/workflows/ingest`: Core logic for document loading and OCR orchestration.
    *   `intelligent_orchestrator.py`: Main routing logic.
    *   `document_detector.py`: Heuristics for PDF type detection.
    *   `ocr/`: OCR engine implementations.
*   `tests/`: Comprehensive test suite (Unit, CLI, E2E, Integration).
*   `data/`: Data storage/models directory.

### Contribution Guidelines
*   Follow PEP 8 style guide.
*   Use Conventional Commits (e.g., `feat:`, `fix:`).
*   Ensure 100% pass on `make ci-all` before submitting PRs.
