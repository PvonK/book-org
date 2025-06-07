# tests/test_book.py

from unittest.mock import patch
from book_org.Book import Book  # Adjust import as necessary


@patch("book_org.Book.extract_isbn_from_filename")
@patch("book_org.Book.fetch_metadata_by_isbn")
@patch("book_org.Book.fetch_metadata_by_title_author")
@patch("book_org.Book.parse_filename")
@patch("book_org.Book.category_fallback")
@patch("book_org.Book.log")  # Avoid cluttering test output
def test_find_metadata_with_isbn(
    mock_log,
    mock_category_fallback,
    mock_parse_filename,
    mock_fetch_by_title_author,
    mock_fetch_by_isbn,
    mock_extract_isbn
):
    # Mock ISBN extraction
    mock_extract_isbn.return_value = "1234567890"

    # Mock metadata fetch by ISBN
    mock_fetch_by_isbn.return_value = {
        "title": "Mock Book",
        "authors": ["Author One"],
        "published": "2020",
        "isbn": "1234567890",
        "categories": ["test-category"]
    }

    book = Book("path/to/Author_One_-_Mock_Book.pdf")
    book.find_metadata()

    assert book.metadata["title"] == "Mock Book"
    mock_fetch_by_isbn.assert_called_once_with("1234567890")
    mock_fetch_by_title_author.assert_not_called()


@patch("book_org.Book.extract_embedded_metadata")
@patch("book_org.Book.extract_isbn_from_filename")
@patch("book_org.Book.fetch_metadata_by_title_author")
@patch("book_org.Book.parse_filename")
@patch("book_org.Book.log")
def test_find_metadata_without_isbn(
    mock_log,
    mock_parse_filename,
    mock_fetch_by_title_author,
    mock_extract_isbn,
    mock_extract_embedded_metadata,
):
    mock_extract_isbn.return_value = None
    mock_extract_embedded_metadata.return_value = None
    mock_parse_filename.return_value = {
        "title": "Mock Title",
        "authors": "Author A"
        }
    mock_fetch_by_title_author.return_value = {
        "title": "Mock Title",
        "authors": ["Author A"],
        "published": "2021",
        "isbn": "9876543210",
        "categories": ["category-a"]
    }

    book = Book("path/to/Mock_Title_by_Author_A.pdf")
    book.find_metadata()

    assert book.metadata["isbn"] == "9876543210"
    mock_fetch_by_title_author.assert_called_once()


def test_set_new_filename_with_metadata():
    book = Book("some/path/file.pdf")
    metadata = {
        "authors": ["Author A", "Author B"],
        "title": "Book Title",
        "published": "2023",
        "isbn": "1234567890"
    }
    book.filename = "dummy.pdf"
    book.set_new_filename(metadata)
    assert book.new_filename.startswith(
        "Author A, Author B - Book Title (2023) [1234567890]"
        )


def test_set_new_filename_without_metadata_and_colon():
    book = Book("some/path/My_Book_ is_here.pdf")
    book.filename = "My_Book_ is_here.pdf"
    book.set_new_filename(None)
    assert "My_Book: is_here" in book.new_filename


def test_set_new_filename_without_metadata_and_slash():
    book = Book("some/path/My/Book.pdf")
    book.filename = "My/Book.pdf"
    book.set_new_filename(None)
    assert "My_Book" in book.new_filename


@patch("book_org.Book.category_fallback")
def test_set_categories_with_metadata(mock_fallback):
    book = Book("path/to/book.pdf")
    book.metadata = {"title": "Test Book", "categories": ["science"]}
    book.set_categories()
    assert book.categories == ["science"]
    mock_fallback.assert_not_called()


@patch("book_org.Book.category_fallback")
def test_set_categories_without_metadata(mock_fallback):
    mock_fallback.return_value = ["fallback-cat"]
    book = Book("path/to/book.pdf")
    book.new_filename = "test_book.pdf"
    book.set_categories()
    assert book.categories == ["no-metadata", "fallback-cat"]


def test_set_new_path_with_categories():
    book = Book("some/path/file.pdf", output_path_dir="test_output")
    book.categories = ["science", "math"]
    book.new_filename = "file.pdf"
    book.set_new_path()
    assert book.new_path == "test_output/science"
    assert book.new_fullpath == "test_output/science/file.pdf"


@patch("book_org.Book.extract_embedded_metadata")
@patch("book_org.Book.extract_isbn_from_filename")
@patch("book_org.Book.fetch_metadata_by_isbn")
@patch("book_org.Book.fetch_metadata_by_title_author")
@patch("book_org.Book.log")
def test_find_metadata_with_embedded_isbn(
    mock_log,
    mock_fetch_by_title_author,
    mock_fetch_by_isbn,
    mock_extract_isbn,
    mock_extract_embedded,
):
    # No ISBN in filename
    mock_extract_isbn.return_value = None

    # Embedded metadata with ISBN
    mock_extract_embedded.return_value = {
        "isbn": "1111222233334",
        "title": "Embedded Book",
        "author": "Embedded Author"
    }

    mock_fetch_by_isbn.return_value = {
        "title": "Embedded Book",
        "authors": ["Embedded Author"],
        "isbn": "1111222233334",
        "published": "2024",
        "categories": ["embedded-cat"]
    }

    book = Book("path/to/ebook.pdf")
    book.find_metadata()

    assert book.metadata["title"] == "Embedded Book"
    assert mock_fetch_by_isbn.call_count == 1
    assert mock_fetch_by_title_author.call_count == 0


@patch("book_org.Book.extract_embedded_metadata")
@patch("book_org.Book.extract_isbn_from_filename")
@patch("book_org.Book.fetch_metadata_by_title_author")
@patch("book_org.Book.fetch_metadata_by_isbn")
@patch("book_org.Book.log")
def test_find_metadata_with_embedded_title_author_only(
    mock_log,
    mock_fetch_by_isbn,
    mock_fetch_by_title_author,
    mock_extract_isbn,
    mock_extract_embedded
):
    mock_extract_isbn.return_value = None

    # Embedded metadata without ISBN
    mock_extract_embedded.return_value = {
        "title": "No ISBN Title",
        "author": "Author Unknown"
    }

    mock_fetch_by_title_author.return_value = {
        "title": "No ISBN Title",
        "authors": ["Author Unknown"],
        "published": "2022",
        "isbn": "0000000000",
        "categories": ["fallback-cat"]
    }

    book = Book("path/to/fallback.pdf")
    book.find_metadata()

    assert book.metadata["isbn"] == "0000000000"
    assert mock_fetch_by_isbn.call_count == 0
    assert mock_fetch_by_title_author.call_count == 1


@patch("book_org.Book.category_fallback")
def test_set_categories_no_metadata_no_fallback(mock_fallback):
    mock_fallback.return_value = []
    book = Book("path/to/book.pdf")
    book.metadata = None
    book.new_filename = "test_book.pdf"
    book.set_categories()
    assert book.categories == ["no-metadata"]
