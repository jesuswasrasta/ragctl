"""Search command for ragctl CLI."""
import json
import time
from typing import Optional
from typing_extensions import Annotated

import typer
from rich.markdown import Markdown

from src.core.cli.utils.display import (
    console,
    print_success,
    print_error,
    print_warning,
    display_stats
)


def search_command(
    query: Annotated[
        str,
        typer.Argument(help="Search query text")
    ],
    collection: Annotated[
        str,
        typer.Option(
            "--collection", "-c",
            help="Qdrant collection name"
        )
    ] = "atlas_chunks",
    top_k: Annotated[
        int,
        typer.Option(
            "--top-k", "-k",
            help="Number of results to return",
            min=1,
            max=100
        )
    ] = 5,
    threshold: Annotated[
        Optional[float],
        typer.Option(
            "--threshold", "-t",
            help="Minimum similarity score threshold (0.0-1.0)",
            min=0.0,
            max=1.0
        )
    ] = None,
    qdrant_url: Annotated[
        str,
        typer.Option(
            "--qdrant-url",
            help="Qdrant server URL"
        )
    ] = "http://localhost:6333",
    json_output: Annotated[
        bool,
        typer.Option(
            "--json-output", "-j",
            help="Output results in JSON format"
        )
    ] = False,
) -> None:
    """
    Retrieve documents from vector store using semantic search.

    This command performs a semantic search directly against the Qdrant vector store.
    It generates an embedding for your query and finds the most similar chunks.

    \b
    Examples:
        # Basic search
        ragctl search "machine learning applications"

        # Search in specific collection
        ragctl search "deep learning" --collection my_docs

        # Get more results
        ragctl search "neural networks" --top-k 10

        # Filter by relevance score
        ragctl search "transformers" --threshold 0.75

        # Output as JSON (for parsing)
        ragctl search "RAG systems" --json-output > results.json
    """
    # Import VectorStore here (lazy import)
    try:
        from src.core.vector import QdrantVectorStore, VectorStoreConfig
    except ImportError as e:
        print_error(f"Failed to import vector store dependencies: {e}")
        print_warning("This may be due to NumPy/scipy compatibility issues.")
        raise typer.Exit(code=1)

    # Configure Qdrant
    if not json_output:
        console.print(f"\n[bold]Configuring search...[/bold]")
        display_stats({
            "Query": query,
            "Collection": collection,
            "Top K": top_k,
            "Threshold": threshold or "None",
            "Qdrant URL": qdrant_url
        })

    config = VectorStoreConfig()
    config.url = qdrant_url
    config.index_name = collection

    # Initialize vector store
    try:
        if not json_output:
            with console.status("[bold green]Connecting to Qdrant..."):
                vector_store = QdrantVectorStore(config)
                vector_store.connect()
        else:
            vector_store = QdrantVectorStore(config)
            vector_store.connect()

    except Exception as e:
        print_error(f"Failed to connect to Qdrant: {e}")
        print_warning("Make sure Qdrant is running:")
        console.print("  [cyan]→[/cyan] docker-compose up -d")
        console.print("  [cyan]→[/cyan] or check the Qdrant URL")
        raise typer.Exit(code=1)

    # Perform search
    start_time = time.time()
    try:
        if not json_output:
            with console.status("[bold green]Searching..."):
                results = vector_store.search_by_text(
                    query=query,
                    top_k=top_k,
                    score_threshold=threshold
                )
        else:
            results = vector_store.search_by_text(
                query=query,
                top_k=top_k,
                score_threshold=threshold
            )
    except Exception as e:
        print_error(f"Search failed: {e}")
        raise typer.Exit(code=1)
    
    search_time = time.time() - start_time

    # Output results
    if json_output:
        output_data = {
            "query": query,
            "collection": collection,
            "results_count": len(results),
            "search_time_seconds": search_time,
            "results": results
        }
        console.print_json(data=output_data)
        return

    # Display results in Markdown
    console.print("\n")
    print_success(f"Found {len(results)} results in {search_time:.3f}s")
    
    if not results:
        print_warning("No results found")
        console.print("  Try:")
        console.print("    • Lowering the threshold")
        console.print("    • Using different keywords")
        console.print("    • Checking if the collection name is correct")
        return

    for i, res in enumerate(results, 1):
        score = res.get('score', 0.0)
        chunk_id = res.get('id', 'N/A')
        text = res.get('text', '')
        metadata = res.get('metadata', {})
        source = metadata.get('source_file', metadata.get('source', 'Unknown'))
        page = metadata.get('page_number', metadata.get('page', 'N/A'))
        
        # Color-code scores
        score_color = "green" if score > 0.7 else "yellow" if score > 0.5 else "white"
        
        console.rule(f"[bold cyan]Result {i}[/bold cyan] (Score: [{score_color}]{score:.3f}[/{score_color}])")
        
        # Metadata section
        meta_info = f"- **Source:** `{source}`\n- **Page:** `{page}`\n- **Chunk ID:** `{chunk_id}`"
        console.print(Markdown(meta_info))
        console.print()
        
        # Text content
        console.print(Markdown(f"### Content\n\n{text}"))
        console.print()

