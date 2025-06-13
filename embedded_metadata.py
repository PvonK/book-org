import re

from typing import Optional, Dict

from .formatter import log
from .extractor import extract_file_extension

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
    ext = extract_file_extension(file_path)[1]
    if ext == ".pdf" and fitz:
        return extract_pdf_metadata(file_path)
    elif ext == ".epub" and epub:
        return extract_epub_metadata(file_path)
    else:
        return {}


def extract_pdf_metadata(file_path: str) -> Dict[str, Optional[str]]:
    meta = {
        "title": None,
        "author": None,
        "isbn": None,
        "date": None,
        # "publisher": None,
    }

    with fitz.open(file_path) as doc:
        pdf_meta = doc.metadata or {}

        meta['title'] = pdf_meta.get('title')
        meta['author'] = pdf_meta.get('author')
        meta['date'] = pdf_meta.get('creationDate') or pdf_meta.get('modDate')
        # meta['publisher'] = pdf_meta.get('producer')

        # Try to extract ISBN from first 3 pages (or less if theres not 3)
        for page in doc[:min(3, len(doc))]:
            text = page.get_text()
            if not meta['isbn']:
                meta['isbn'] = extract_isbn_from_text(text)
            # if not meta['publisher']:
            #     meta['publisher'] = extract_publisher_from_text(text)

    return meta


def extract_epub_metadata(file_path: str) -> Dict[str, Optional[str]]:
    meta = {
        "title": None,
        "author": None,
        "isbn": None,
        "date": None,
        # "publisher": None,
    }

    book = epub.read_epub(file_path)

    def get_dc(tag):
        val = book.get_metadata('DC', tag)
        return val[0][0] if val else None

    meta['title'] = get_dc('title')
    meta['author'] = get_dc('creator')
    meta['date'] = get_dc('date')
    # meta['publisher'] = get_dc('publisher')

    # Fallback to scanning content for ISBN/publisher if missing
    for item in book.items:
        if item.get_type() == epub.EpubHtml:
            text = item.get_body_content().decode(errors='ignore')

            if not meta['isbn']:
                meta['isbn'] = extract_isbn_from_text(text)
            # if not meta['publisher']:
            #    meta['publisher'] = extract_publisher_from_text(text)

            if meta['isbn']:  # and meta['publisher']:
                break

    return meta


def extract_isbn_from_text(text: str) -> Optional[str]:
    match = re.search(
        r"\b(97[89][-\s]?\d{1,5}[-\s]?\d{1,7}[-\s]?\d{1,7}[-\s]?\d)\b",
        text
        )
    if match:
        return re.sub(r"[-\s]", "", match.group(1))
    return None


def extract_publisher_from_text(text: str) -> Optional[str]:
    # Look for common publisher patterns
    patterns = [
        r"Published by ([A-Z][\w&\s,.'-]{3,50})",
        r"Publisher[:\s]+([A-Z][\w&\s,.'-]{3,50})",
        r"\n([A-Z][\w&\s,.'-]{3,50})\n.*\bPublishing\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None
