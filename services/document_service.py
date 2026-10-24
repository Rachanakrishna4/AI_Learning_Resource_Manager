
from pathlib import Path
from pypdf import PdfReader


def extract_text_from_pdf(file_path: str) -> str:
    """Extract readable text from a PDF file."""

    path = Path(file_path)

    # Check whether the file exists
    if not path.exists():
        raise FileNotFoundError("PDF file was not found.")

    # Check whether it is a PDF
    if path.suffix.lower() != ".pdf":
        raise ValueError("Please provide a PDF file.")

    # Open the PDF
    reader = PdfReader(str(path))

    # Read the text from each page
    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)

    # Combine all pages into one text string
    full_text = "\n".join(pages).strip()

    if not full_text:
        raise ValueError(
            "No readable text found. The PDF may be scanned."
        )

    return full_text

def chunk_text(
    text: str,
    chunk_size: int = 200,
    overlap: int = 30
) -> list[str]:
    """Split text into word-based chunks with some overlap."""

    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "Overlap must be non-negative and smaller than chunk size."
        )

    words = text.split()
    chunks = []
    step = chunk_size - overlap

    for start in range(0, len(words), step):
        chunk_words = words[start:start + chunk_size]

        if not chunk_words:
            break

        chunks.append(" ".join(chunk_words))

        if start + chunk_size >= len(words):
            break

    return chunks

