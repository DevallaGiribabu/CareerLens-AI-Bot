import fitz
from pathlib import Path


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """Extract text from a PDF file."""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    text_chunks = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text = page.get_text("text")
            if text:
                text_chunks.append(text)

    return "\n\n".join(text_chunks).strip()
