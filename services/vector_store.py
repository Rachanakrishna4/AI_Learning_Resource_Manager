
from pathlib import Path

import chromadb

# Find the main project folder
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Save the vector database inside data/chroma
CHROMA_DIR = PROJECT_DIR / "data" / "chroma"
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# Create a persistent ChromaDB client
client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

# Create or open our collection
collection = client.get_or_create_collection(
    name="study_chunks",
    metadata={"hnsw:space": "cosine"}
)


def add_chunks(chunks, embeddings, source_name):
    """Save text chunks and their embeddings in ChromaDB."""

    if len(chunks) != len(embeddings):
        raise ValueError(
            "The number of chunks must match the number of embeddings."
        )

    if not chunks:
        return 0

    # Give each chunk a unique ID
    file_name = Path(source_name).stem
    ids = [
        f"{file_name}-{i}"
        for i in range(len(chunks))
    ]

    # Store the original filename and chunk number
    metadata = [
        {
            "source": Path(source_name).name,
            "chunk_index": i
        }
        for i in range(len(chunks))
    ]

    # Save text, vectors and metadata together
    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings.tolist(),
        metadatas=metadata
    )

    return len(chunks)


def get_collection_count():
    """Return the number of stored chunks."""
    return collection.count()
