from unittest.mock import patch
from book_org.parser import clean_filename
from book_org.parser import parse_annas_filename
from book_org.parser import parse_filename


# ---------------------
# Tests for clean_filename
# ---------------------


def test_clean_filename_replacements():
    assert clean_filename("A_Book_–_Title__ ") == "A Book - Title"
    assert clean_filename("Multiple___Spaces") == "Multiple Spaces"
    assert clean_filename("Underscore_ Space_ ") == "Underscore: Space"

# ---------------------
# Tests for parse_annas_filename
# ---------------------


def test_parse_annas_filename():
    filename = "My Book -- John Doe.pdf"
    result = parse_annas_filename(filename)
    assert result == {"title": "My Book", "authors": "John Doe"}

# ---------------------
# Tests for parse_filename
# ---------------------


@patch("book_org.parser.extract_series", return_value=None)
@patch("book_org.parser.extract_year", return_value=None)
def test_parse_filename_title_only(mock_extract_year, mock_extract_series):
    filename = "Interesting Book.pdf"
    result = parse_filename(filename)
    assert result['title'] == "Interesting Book"
    assert result['authors'] is None
    assert result['extension'] == ".pdf"


@patch("book_org.parser.extract_series", return_value=None)
@patch("book_org.parser.extract_year", return_value=None)
def test_parse_filename_with_author_and_title(
        mock_extract_year,
        mock_extract_series
        ):
    filename = "Jane Doe - A Tale of Code.pdf"
    result = parse_filename(filename)
    assert result['authors'] == "Jane Doe"
    assert result['title'] == "A Tale of Code"
    assert result['extension'] == ".pdf"


@patch("book_org.parser.extract_series", return_value=None)
@patch("book_org.parser.extract_year", return_value=None)
def test_parse_filename_by_author(mock_extract_year, mock_extract_series):
    filename = "A Tale of Two Parsers by John Dev.epub"
    result = parse_filename(filename)
    assert result['authors'] == "John Dev"
    assert result['title'] == "A Tale of Two Parsers"
    assert result['extension'] == ".epub"


@patch(
    "book_org.parser.extract_series",
    return_value=("My Series", "Book Title")
    )
@patch("book_org.parser.extract_year", return_value=None)
def test_parse_filename_with_series(mock_extract_year, mock_extract_series):
    filename = "Book Title.pdf"
    result = parse_filename(filename)
    assert result['series'] == "My Series"
    assert result['title'] == "Book Title"


@patch("book_org.parser.extract_series", return_value=None)
@patch(
    "book_org.parser.extract_year",
    return_value=("2020", "O'Reilly", "Book Without Year")
    )
def test_parse_filename_with_year_and_publisher(
        mock_extract_year,
        mock_extract_series
        ):
    filename = "Book Without Year.pdf"
    result = parse_filename(filename)
    assert result['year'] == "2020"
    assert result['publisher'] == "O'Reilly"
    assert result['title'] == "Book Without Year"


@patch("book_org.parser.extract_series", return_value=None)
@patch("book_org.parser.extract_year", return_value=None)
def test_parse_filename_with_year_only(mock_extract_year, mock_extract_series):
    filename = "Book With Year (2021).pdf"
    result = parse_filename(filename)
    assert result['year'] == "2021"
    assert result['title'] == "Book With Year"


@patch("book_org.parser.extract_series", return_value=None)
@patch("book_org.parser.extract_year", return_value=None)
def test_parse_filename_with_volume(mock_extract_year, mock_extract_series):
    filename = "Series Book Volume 3.pdf"
    result = parse_filename(filename)
    assert result['volume'] == "3"


@patch("book_org.parser.extract_series", return_value=None)
@patch("book_org.parser.extract_year", return_value=None)
def test_parse_filename_removes_libgen_zlib(
        mock_extract_year,
        mock_extract_series
        ):
    filename = "Author - Book Title - for(z-lib.org).pdf"
    result = parse_filename(filename)
    assert "z-lib" not in result['title']
    assert result['authors'] == "Author"
    assert result['title'] == "Book Title"


@patch("book_org.parser.extract_series", return_value=None)
@patch("book_org.parser.extract_year", return_value=None)
def test_parse_filename_annas_archive_redirects(
        mock_extract_year,
        mock_extract_series
        ):
    filename = "Sample Book -- Jane Doe -- Anna’s Archive.pdf"
    result = parse_filename(filename)
    assert result['title'] == "Sample Book"
    assert result['authors'] == "Jane Doe"
