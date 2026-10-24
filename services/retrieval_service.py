from pathlib import Path
from chromadb.utils import embedding_functions


import chromadb

BASE_DIR = Path(__file__).parent.parent
NOTES_DIR = BASE_DIR / "notes"
CHUNK_SIZE = 800
OVERLAP = 100

_client = chromadb.PersistentClient(path=str(BASE_DIR / "chroma_db"))
_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
_collection = _client.get_or_create_collection("notes", embedding_function=_ef)


def _chunk(text: str) -> list[str]:
    chunks, start = [], 0
    while start < len(text):
        piece = text[start:start + CHUNK_SIZE].strip()
        if piece:
            chunks.append(piece)
        start += CHUNK_SIZE - OVERLAP
    return chunks


def index_notes() -> int:
    """Re-index all .txt/.md files in the notes folder."""
    NOTES_DIR.mkdir(exist_ok=True)
    ids, docs, metas = [], [], []
    for path in sorted(NOTES_DIR.glob("*")):
        if path.suffix.lower() not in {".txt", ".md"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for i, chunk in enumerate(_chunk(text)):
            ids.append(f"{path.name}-{i}")
            docs.append(chunk)
            metas.append({"source": path.name, "chunk_index": i})
    if ids:
        _collection.upsert(ids=ids, documents=docs, metadatas=metas)
    return len(ids)


def search_notes(question: str, top_k: int = 3) -> list[dict]:
    if _collection.count() == 0:
        index_notes()
    if _collection.count() == 0:
        raise ValueError("No notes found. Add .txt or .md files to the 'notes' folder.")

    result = _collection.query(
        query_texts=[question],
        n_results=min(top_k, _collection.count()),
    )
    return [
        {
            "text": doc,
            "source": meta["source"],
            "chunk_index": meta["chunk_index"],
            "distance": dist,
        }
        for doc, meta, dist in zip(
            result["documents"][0], result["metadatas"][0], result["distances"][0]
        )
    ]