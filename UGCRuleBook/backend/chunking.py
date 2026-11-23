import re
from pathlib import Path

import pytesseract
from bs4 import BeautifulSoup
from pdf2image import convert_from_path
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFPopplerTimeoutError,
)
from pypdf import PdfReader
from pypdf.errors import PdfReadError

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\bde\s+nial\b", "denial", text, flags=re.IGNORECASE)
    return text.strip()


def extract_page_with_ocr(pdf_path, page_number):
    try:
        images = convert_from_path(
            str(pdf_path),
            dpi=200,
            first_page=page_number,
            last_page=page_number
        )

        if not images:
            return ""

        text = pytesseract.image_to_string(
            images[0],
            lang="eng+hin"
        )

        return clean_text(text)

    except (
        PDFInfoNotInstalledError,
        PDFPageCountError,
        PDFPopplerTimeoutError,
        pytesseract.TesseractNotFoundError,
        pytesseract.TesseractError,
        OSError,
    ) as error:
        print(f"OCR failed for {pdf_path.name}, page {page_number}: {error}")
        return ""


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
    current_section = None

    try:
        reader = PdfReader(str(pdf_path))

        title = (
            reader.metadata.title
            if reader.metadata and reader.metadata.title
            else pdf_path.stem.replace("_", " ").title()
        )

        for page_number, page in enumerate(reader.pages, start=1):

            text = page.extract_text() or ""

            if len(text.strip()) < 50:
                print(f"Using OCR: {pdf_path.name}, page {page_number}")
                text = extract_page_with_ocr(pdf_path, page_number)

            text = clean_text(text)

            if not text:
                print(f"No text found: {pdf_path.name}, page {page_number}")
                continue

            metadata = {
                "source": pdf_path.name,
                "page": page_number,
                "title": title
            }

            if pdf_path.name == "sexual_harassment_2015.pdf":
                section_markers = (
                    (
                        "responsibilities of the higher educational institution",
                        "Responsibilities of the Higher Educational Institution"
                    ),
                    (
                        "grievance redressal mechanism",
                        "Regulation 4: Grievance redressal mechanism"
                    ),
                    (
                        "responsibilities of internal complaints committee",
                        "Responsibilities of the Internal Complaints Committee (ICC)"
                    ),
                    (
                        "the process for making complaint and conducting inquiry",
                        "Regulation 6: Process for making complaint and conducting inquiry"
                    )
                )
                page_sections = [current_section] if current_section else []
                matches = []
                for marker, section in section_markers:
                    position = text.lower().find(marker)
                    if position >= 0:
                        matches.append((position, section))

                for _, section in sorted(matches):
                    if section not in page_sections:
                        page_sections.append(section)

                if matches:
                    current_section = max(matches, key=lambda match: match[0])[1]
                if page_sections:
                    metadata["section"] = " | ".join(page_sections)

            documents.append({
                "text": text,
                "metadata": metadata
            })

        print("Processed PDF:", pdf_path.name)

    except (PdfReadError, OSError) as error:
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

    except (OSError, UnicodeDecodeError) as error:
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
