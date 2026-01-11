# RAG Pipeline Architecture & Configuration Guide

This document provides a comprehensive overview of the Retrieval-Augmented Generation (RAG) pipeline implemented in `ragctl`. It details every step, from document ingestion to vector storage, specifying the tools used and how to configure them, including local model usage with Ollama.

## 1. Pipeline Overview

The `ragctl` pipeline consists of the following sequential stages:

1.  **Ingestion & Document Detection**: Loading documents and identifying their type (text-based, scanned, hybrid, image).
2.  **OCR & Correction**: Extracting text from images/scanned PDFs and correcting errors using rules and AI.
3.  **Chunking**: Splitting text into semantic units suitable for retrieval.
4.  **Embedding**: Converting text chunks into vector representations.
5.  **Storage (Indexing)**: Storing vectors and metadata in a vector database (Qdrant) for fast retrieval.

---

## 2. Detailed Pipeline Steps

### Step 1: Ingestion & Document Detection

**Goal**: Load the document and determine the best strategy for text extraction.

*   **Tool Used**: `IntelligentDocumentOrchestrator` (`src/workflows/ingest/intelligent_orchestrator.py`)
*   **Logic**:
    *   **Detection**: Uses `DocumentTypeDetector` to analyze PDFs.
        *   Checks for text layers (text-based).
        *   Checks for images (scanned).
        *   Checks text density (hybrid).
    *   **Routing**:
        *   **Text-based PDF**: Uses `PyMuPDF` (via `PyMuPDFLoader`) for fast, direct text extraction.
        *   **Scanned PDF/Image**: Uses `EasyOCR` (or `PaddleOCR` fallback) for Optical Character Recognition.
        *   **Hybrid PDF**: Tries `PyMuPDF` first; falls back to OCR if extracted text density is low (< 200 chars/page).
        *   **Images**: Direct OCR.

**Configuration**:
*   **Force OCR**: You can force OCR even on text-based PDFs using the `--force-ocr` flag in the CLI.

### Step 2: OCR & Correction

**Goal**: accurate text extraction from non-digital documents and fixing OCR errors.

*   **Tools Used**:
    *   **Engines**: `EasyOCR` (default), `PaddleOCR` (fallback), `Tesseract` (fallback), `Qwen-VL` (advanced).
    *   **Correction**: `OCRCorrectionPipeline` (`src/workflows/ingest/ocr_correction_pipeline.py`).
*   **Correction Pipeline**:
    1.  **Rule-based**: Applies regex and heuristic rules (e.g., fixing spacing, merging hyphenated words). Uses `AggressiveOCRCorrector` or `OCRCorrectorUnstructured`.
    2.  **AI-based (LLM)**: Uses a Language Model to fix semantic and grammatical errors.
        *   **Trigger**: Can be configured to run always (`AI_ONLY`), only when OCR confidence is low (`HYBRID` + confidence threshold), or never (`RULES_ONLY`).
        *   **Model**: Can use local models (Ollama) or remote APIs (OpenAI, Anthropic).

**Configuration (`config.yml` or CLI)**:
*   **Enable Advanced OCR**: `ocr.use_advanced_ocr: true` (uses Qwen-VL).
*   **Dictionary Threshold**: `ocr.dictionary_threshold: 0.3` (triggers advanced OCR if recognized word count is low).
*   **Correction Strategy**:
    *   `hybrid` (default): Rules + AI if needed.
    *   `rules_only`: No LLM.
    *   `ai_only`: LLM for everything.
*   **AI Correction Provider**: Configure under `llm` section (see below).

### Step 3: Chunking

**Goal**: Split the continuous text into smaller, meaningful segments (chunks) for retrieval.

*   **Tool Used**: `AtlasChunker` (`src/core/chunk/langchain_chunker.py`) which wraps LangChain's splitters.
*   **Strategies**:
    1.  **`semantic` (default)**: Uses `RecursiveCharacterTextSplitter`. Splits by separators (paragraphs `

`, newlines `
`, sentences `. `, etc.) to keep related text together.
    2.  **`token`**: Uses `TokenTextSplitter`. Splits strictly by token count (hard breaks).
    3.  **`sentence`**: Splits by sentence boundaries.
*   **Preprocessing**:
    *   `TextPreprocessor` cleans text before chunking (fixes common PDF extraction artifacts like missing spaces `Ala` -> `A la`, removing headers/footers).

**Configuration**:
*   **Strategy**: `chunking.strategy` (`semantic`, `token`, `sentence`).
*   **Size**: `chunking.max_tokens` (e.g., `400`).
*   **Overlap**: `chunking.overlap` (e.g., `50` to maintain context across boundaries).

### Step 4: Embedding

**Goal**: Convert text chunks into vector embeddings (lists of floating-point numbers) that capture semantic meaning.

*   **Tool Used**: `sentence-transformers` (HuggingFace) via `src/core/vector/embeddings.py` and `src/workflows/ml/embeddings.py`.
*   **Model**: Defaults to `sentence-transformers/all-MiniLM-L6-v2` (fast, efficient).
*   **Process**:
    1.  Batches chunks.
    2.  Runs them through the model.
    3.  Normalizes vectors (optional, but recommended for cosine similarity).

**Configuration**:
*   **Model**: Can be changed via code or potentially config (defaults to `all-MiniLM-L6-v2`).
*   **Batch Size**: configurable for performance.

### Step 5: Storage (Indexing)

**Goal**: Store embeddings and metadata for fast similarity search.

*   **Tool Used**: `Qdrant` (Vector Database) via `src/core/vector/qdrant_store.py`.
*   **Operation**:
    *   **Upsert**: Stores vectors + payload (original text, document source, page number, etc.).
    *   **ID Generation**: deterministic UUID v5 based on chunk content/ID to prevent duplicates.
*   **Deployment**:
    *   **Local/Memory**: If no URL is provided, runs in-memory.
    *   **Server**: Connects to a Qdrant instance via URL/API Key.

**Configuration**:
*   **URL**: `qdrant_url` (e.g., `http://localhost:6333`).
*   **Collection Name**: `qdrant_collection` (e.g., `my-docs`).

### Step 6: Retrieval (Search)

**Goal**: Find the most relevant document chunks based on a natural language query.

*   **Tool Used**: `QdrantStore.search_by_text` (`src/core/vector/qdrant_store.py`).
*   **Implementation Status**:
    *   **Logic**: Fully implemented in the Python core.
    *   **CLI**: The `ragctl search` command is currently hidden and configured to call an external API server. Direct CLI search is pending.
*   **Process**:
    1.  **Vectorization**: The search query is converted into an embedding using the same model used during ingestion (`sentence-transformers/all-MiniLM-L6-v2`).
    2.  **Similarity Search**: Qdrant performs a Cosine Similarity search to find the $K$ most similar vectors.
    3.  **Result Formatting**: Returns chunks with text, metadata, and a similarity score (0.0 to 1.0).

**Configuration**:
*   **Top K**: `top_k` (number of results, default: 10).
*   **Threshold**: `score_threshold` (e.g., `0.7` to filter out low-relevance results).

---

## 3. Configuring Models & Ollama (Local LLMs)

You can configure `ragctl` to use local models via Ollama for **OCR Correction** and **Text Analysis**.

### Prerequisites
1.  **Install Ollama**: [ollama.com](https://ollama.com)
2.  **Pull Models**:
    ```bash
    ollama pull mistral   # For text correction
    ollama pull qwen2.5-vl-7b # For advanced OCR (if using Qwen-VL)
    ```

### Configuration File (`~/.ragctl/config.yml`)

Create or edit your config file to point to your local Ollama instance.

```yaml
# LLM Configuration for OCR Correction & Analysis
llm:
  use_llm: true          # Enable AI features
  provider: ollama       # Use local Ollama
  url: http://localhost:11434  # Default Ollama URL
  model: mistral:latest  # Model to use (must be pulled in Ollama)
  timeout: 60            # Increase for slower local models
  temperature: 0.1       # Keep low for factual corrections

# OCR Configuration (Optional: Advanced Vision)
ocr:
  use_advanced_ocr: false  # Set to true to use Vision-Language Models
  # If true, configure Qwen-VL below:
  qwen_vl_url: http://localhost:11434
  qwen_vl_model: qwen2.5-vl-7b
```

### Environment Variables

Alternatively, use environment variables:

```bash
export ATLAS_USE_LLM=true
export ATLAS_LLM_PROVIDER=ollama
export ATLAS_LLM_URL=http://localhost:11434
export ATLAS_LLM_MODEL=mistral:latest
```

### Usage Example with Local LLM

```bash
# Process a scanned PDF with AI correction enabled using local Mistral
ragctl chunk scanned_doc.pdf \
  --advanced-ocr \
  --output result.json
```

If `ocr.use_advanced_ocr` is enabled, it may attempt to use a Vision-Language Model. Ensure you have a compatible model (like `qwen2.5-vl`) loaded in Ollama if you use that specific feature, or stick to the default `EasyOCR` + `Mistral` (text-only correction) pipeline.
