import re

from typing import Optional, Dict
from pathlib import Path

from .formatter import log

try:
    import fitz  # PyMuPDF
except ImportError:
    log("[ERROR]", "failed to import fitz")
    fitz = None

try:
    from ebooklib import epub
except ImportError:
    log("[ERROR]", "failed to import ebooklib")
    epub = None


def extract_metadata(file_path: str) -> Dict[str, Optional[str]]:
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf" and fitz:
        return extract_pdf_metadata(file_path)
    elif ext == ".epub" and epub:
        return extract_epub_metadata(file_path)
    else:
        return {}  # Fallback or unsupported format


def extract_pdf_metadata(file_path: str) -> Dict[str, Optional[str]]:
    meta = {}
    with fitz.open(file_path) as doc:
        pdf_meta = doc.metadata or {}
        meta['title'] = pdf_meta.get('title')
        meta['author'] = pdf_meta.get('author')

        # Try to extract ISBN from first 3 pages (or less if theres not 3)
        for page in doc[:min(3, len(doc))]:
            text = page.get_text()
            isbn = extract_isbn_from_text(text)
            if isbn:
                meta['isbn'] = isbn
                break
    return meta


def extract_epub_metadata(file_path: str) -> Dict[str, Optional[str]]:
    meta = {}
    book = epub.read_epub(file_path)

    title = book.get_metadata('DC', 'title')
    author = book.get_metadata('DC', 'creator')
    meta['title'] = title[0][0] if title else None
    meta['author'] = author[0][0] if author else None

    # EPUBs rarely have ISBNs in metadata, may need to extract from content
    for item in book.items:
        if item.get_type() == epub.EpubHtml:
            text = item.get_body_content().decode(errors='ignore')
            isbn = extract_isbn_from_text(text)
            if isbn:
                meta['isbn'] = isbn
                break
    return meta


def extract_isbn_from_text(text: str) -> Optional[str]:
    match = re.search(
        r"(97[89][-\s]?\d{1,5}[-\s]?\d{1,7}[-\s]?\d{1,7}[-\s]?\d)",
        text
        )
    if match:
        return match.group(1).replace(" ", "").replace("-", "")
    return None
