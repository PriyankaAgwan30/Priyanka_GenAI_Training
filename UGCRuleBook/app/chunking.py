
import re
from pathlib import Path

from pypdf import PdfReader
from bs4 import BeautifulSoup


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\bde\s+nial\b", "denial", text, flags=re.IGNORECASE)
    return text.strip()


def split_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):

    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size")

    text = clean_text(text)

    chunks = []
    start = 0

    while start < len(text):

        end = min(start + chunk_size, len(text))

        if end < len(text):
            boundary = text.rfind(" ", start, end)

            if boundary > start:
                end = boundary

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks


def get_pdf_documents(pdf_path):

    documents = []

    try:
        reader = PdfReader(str(pdf_path))

        title = (
            reader.metadata.title
            if reader.metadata and reader.metadata.title
            else pdf_path.stem.replace("_", " ").title()
        )

        for page_number, page in enumerate(reader.pages, start=1):

            text = page.extract_text() or ""

            if not text.strip():
                continue

            documents.append({
                "text": clean_text(text),
                "metadata": {
                    "source": pdf_path.name,
                    "page": page_number,
                    "title": title
                }
            })

        print("Processed PDF:", pdf_path.name)

    except Exception as error:
        print("Error reading PDF:", pdf_path.name, error)

    return documents


def get_html_documents(html_path):

    documents = []

    try:
        html = html_path.read_text(encoding="utf-8")

        soup = BeautifulSoup(html, "html.parser")

        title = (
            soup.title.get_text(strip=True)
            if soup.title
            else html_path.stem.replace("_", " ").title()
        )

        for unwanted in soup(["script", "style", "noscript"]):
            unwanted.decompose()

        text = soup.get_text(separator="\n")

        text = clean_text(text)

        if text:
            documents.append({
                "text": text,
                "metadata": {
                    "source": html_path.name,
                    "page": 1,
                    "title": title
                }
            })

        print("Processed HTML:", html_path.name)

    except Exception as error:
        print("Error reading HTML:", html_path.name, error)

    return documents


def load_documents():

    documents = []

    for pdf_path in sorted(RAW_DIR.glob("*.pdf")):
        documents.extend(get_pdf_documents(pdf_path))

    for html_path in sorted(RAW_DIR.glob("*.html")):
        documents.extend(get_html_documents(html_path))

    return documents


def chunk_documents(chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    documents = load_documents()
    all_chunks = []

    for document in documents:
        text_chunks = split_text(
            document["text"],
            chunk_size=chunk_size,
            overlap=overlap
        )

        for index, chunk in enumerate(text_chunks, start=1):
            all_chunks.append({
                "id": (
                    f"{document['metadata']['source']}_"
                    f"{document['metadata']['page']}_"
                    f"{index}"
                ),
                "text": chunk,
                "metadata": document["metadata"].copy()
            })

    return all_chunks


if __name__ == "__main__":

    chunks = chunk_documents()

    print("\nTotal chunks generated:", len(chunks))

    for chunk in chunks[:5]:
        print("\nChunk ID:", chunk["id"])
        print("Metadata:", chunk["metadata"])
        print("Text:", chunk["text"][:200])
