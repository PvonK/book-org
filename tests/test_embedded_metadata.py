import pytest
from unittest.mock import patch, MagicMock
from ebooklib import epub

from book_org.embedded_metadata import (
    extract_metadata,
    extract_pdf_metadata,
    extract_epub_metadata,
    extract_isbn_from_text
)

@pytest.mark.parametrize("text,isbn", [
    ("This book's ISBN is 978-3-16-148410-0", "9783161484100"),
    ("ISBN: 978 0 306 40615 7", "9780306406157"),
    ("No ISBN here", None),
    ("ISBN 979-12-200-5631-0", "9791220056310"),
])
def test_extract_isbn_from_text(text, isbn):
    assert extract_isbn_from_text(text) == isbn


@patch("book_org.embedded_metadata.fitz.open")
def test_extract_pdf_metadata(mock_fitz_open):
    mock_doc = MagicMock()
    mock_doc.__enter__.return_value = mock_doc
    mock_doc.metadata = {'title': 'Test PDF Title', 'author': 'John Doe'}

    mock_page = MagicMock()
    mock_doc.__getitem__.side_effect = lambda idx: [mock_page][idx]
    mock_page.get_text.return_value = "ISBN 978-1-56619-909-4"
    mock_doc.__len__.return_value = 1
    mock_doc.__getitem__.return_value = mock_page
    mock_doc.__iter__.return_value = [mock_page]

    mock_fitz_open.return_value = mock_doc

    result = extract_pdf_metadata("fake.pdf")
    assert result['title'] == "Test PDF Title"
    assert result['author'] == "John Doe"
    assert result['isbn'] == "9781566199094"


@patch("book_org.embedded_metadata.epub.read_epub")
def test_extract_epub_metadata(mock_read_epub):
    mock_book = MagicMock()
    mock_book.get_metadata.side_effect = lambda ns, field: {
        ('DC', 'title'): [("EPUB Title", {})],
        ('DC', 'creator'): [("Jane Author", {})],
    }.get((ns, field), [])

    mock_html_item = MagicMock()
    mock_html_item.get_type.return_value = epub.EpubHtml
    mock_html_item.get_body_content.return_value = b"<html>ISBN 978-0-13-235088-4</html>"

    mock_book.items = [mock_html_item]
    mock_read_epub.return_value = mock_book

    result = extract_epub_metadata("fake.epub")
    assert result['title'] == "EPUB Title"
    assert result['author'] == "Jane Author"
    assert result['isbn'] == "9780132350884"


@patch("book_org.embedded_metadata.extract_pdf_metadata")
def test_extract_metadata_pdf(mock_pdf):
    mock_pdf.return_value = {'title': 'X', 'author': 'Y'}
    result = extract_metadata("test.pdf")
    assert result['title'] == 'X'


@patch("book_org.embedded_metadata.extract_epub_metadata")
def test_extract_metadata_epub(mock_epub):
    mock_epub.return_value = {'title': 'A', 'author': 'B'}
    result = extract_metadata("test.epub")
    assert result['author'] == 'B'


def test_extract_metadata_unknown_format():
    result = extract_metadata("test.txt")
    assert result == {}
