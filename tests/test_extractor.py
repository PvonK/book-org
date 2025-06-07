from book_org.extractor import (
    extract_series,
    extract_year,
    extract_isbn_from_filename,
    extract_isbn_from_industry_ids,
)


def test_extract_series_with_square_brackets():
    name = "[Series Name] Some Book Title"
    result = extract_series(name)
    assert result == ("Series Name", "Some Book Title")


def test_extract_series_with_parentheses():
    name = "(My Series) Another Title"
    result = extract_series(name)
    assert result == ("My Series", "Another Title")


def test_extract_series_no_match():
    name = "No series here"
    result = extract_series(name)
    assert result is None


def test_extract_year_with_publisher():
    name = "Book Title (2021, Wiley)"
    result = extract_year(name)
    assert result == ("2021", "Wiley", "Book Title")


def test_extract_year_with_extra_spaces():
    name = "Book Title (2022,  Springer Nature )"
    result = extract_year(name)
    assert result == ("2022", "Springer Nature", "Book Title")


def test_extract_year_no_match():
    name = "Book Title (No Year, No Publisher)"
    result = extract_year(name)
    assert result is None


def test_extract_isbn_from_filename_isbn13():
    filename = "SomeBook_9781234567897.pdf"
    result = extract_isbn_from_filename(filename)
    assert result == "9781234567897"


def test_extract_isbn_from_filename_isbn10():
    filename = "Book_123456789X.epub"
    result = extract_isbn_from_filename(filename)
    assert result == "123456789X"


def test_extract_isbn_from_filename_no_isbn():
    filename = "NoISBNHere.pdf"
    result = extract_isbn_from_filename(filename)
    assert result is None


def test_extract_isbn_from_industry_ids_with_isbn13():
    identifiers = [
        {"type": "OTHER", "identifier": "0000000000"},
        {"type": "ISBN_13", "identifier": "9781234567897"},
        {"type": "ISBN_10", "identifier": "123456789X"},
    ]
    result = extract_isbn_from_industry_ids(identifiers)
    assert result == "9781234567897"


def test_extract_isbn_from_industry_ids_no_isbn13():
    identifiers = [
        {"type": "OTHER", "identifier": "0000000000"},
        {"type": "ISBN_10", "identifier": "123456789X"},
    ]
    result = extract_isbn_from_industry_ids(identifiers)
    assert result == ""


def test_extract_isbn_from_industry_ids_empty_list():
    identifiers = []
    result = extract_isbn_from_industry_ids(identifiers)
    assert result == ""
