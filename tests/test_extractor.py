import pytest
from book_org.extractor import (
    extract_series,
    extract_year,
    extract_isbn_from_filename,
    extract_isbn_from_industry_ids,
    check_author_in_filename,
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


@pytest.mark.parametrize("authors, title, expected", [
    # Exact match
    (["Isaac Asimov"], "Foundation by Isaac Asimov", True),

    # Match despite case differences
    (["Arthur C. Clarke"], "rendezvous with rama by arthur c clarke", True),

    # Comma-separated author name
    (["Clarke, Arthur C."], "rendezvous with rama by arthur c clarke", True),

    # Partial match with short word excluded (e.g., "Li")
    (["Li"], "Deep Learning by Ian Goodfellow and Li", False),

    # Multiple authors — one matches
    (["Yann LeCun", "Geoffrey Hinton"],
        "AI Revolution by Geoffrey Hinton", True),

    # Multiple authors — none match
    (["Alan Turing", "Ada Lovelace"], "Modern Quantum Computing", False),

    # Author name is a subset of other words in title
    (["Ann"], "Understanding Annual Reports", False),

    # Author name contains special characters
    (["José Ortega y Gasset"],
        "The Revolt of the Masses by Jose Ortega y Gasset", True),

    # Author word appears as substring of longer word
    (["Mark"], "Marketing for Beginners", False),

    # Author name in reversed order
    (["George Orwell"], "1984 by Orwell George", True),

    # Title includes punctuation
    (["Mary Shelley"],
        "Frankenstein: The Modern Prometheus by Mary Shelley", True),

    # Simple direct match
    (["George Orwell"], "1984 by George Orwell", True),

    # Case insensitivity
    (["george orwell"], "1984 by GEORGE ORWELL", True),

    # Punctuation handling
    (["Orwell, George"], "1984 by George Orwell", True),

    # Word length filtering (<3)
    (["A. I. To"], "Handbook To Greatness", False),  # "A", "I", "To" ignored

    # Word length accepted (=<3)
    (["A. I. Tan"], "AI Tan's Handbook", True),  # "A", "I" ignored

    # Substring no match (within longer word)
    (["Smith"], "The Smithsonian Guide", False),

    # Word not in title
    (["Mary Shelley"], "Frankenstein by Unknown", False),

    # Multiple authors, one match
    (["Mary Shelley", "George Orwell"], "1984 by George Orwell", True),

    # Multiple authors, no matches
    (["Isaac Asimov", "Arthur Clarke"], "Dune by Frank Herbert", False),

    # Author partially in title
    (["Arthur C. Clarke"], "The Clarke Equation", True),

    # Hyphenated names
    (["Jean-Paul Sartre"], "A Look at Sartre's Philosophy", True),

    # Words shorter than 3 letters filtered
    (["Li Po"], "Collected Poems of Po", False),  # "Po" ignored

    # Title with numbers and punctuation
    (["Yuval Noah Harari"], "Sapiens: A Brief History of Humankind", False),
    (["Yuval Noah Harari"], "Sapiens by Yuval Harari", True),

    # Long compound last names
    (["Gabriel García Márquez"],
        "One Hundred Years of Solitude by Gabriel Garcia Marquez", True),

    # No Author
    ([],
        "One Hundred Years of Solitude by Gabriel Garcia Marquez", False),

    # None Author
    ([None],
        "One Hundred Years of Solitude by Gabriel Garcia Marquez", False),

])
def test_check_author_in_filename(authors, title, expected):
    assert check_author_in_filename(authors, title) == expected
