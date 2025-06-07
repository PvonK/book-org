# test_fetcher.py

from unittest.mock import patch, MagicMock
from book_org import fetcher


def test_parse_metadata_basic():
    item = {
        "volumeInfo": {
            "title": "Example Book",
            "authors": ["Author One"],
            "publishedDate": "2020-07-01",
            "industryIdentifiers": [
                {"type": "ISBN_13", "identifier": "1234567890123"}
                ],
            "publisher": "Example Publisher",
            "categories": ["Fiction", "Adventure"],
            "imageLinks": {"thumbnail": "http://image.url/thumb.jpg"}
        }
    }
    with patch(
        'book_org.fetcher.extract_isbn_from_industry_ids',
        return_value="1234567890123"
            ):
        metadata = fetcher.parse_metadata(item)
    assert metadata["title"] == "Example Book"
    assert metadata["authors"] == ["Author One"]
    assert metadata["published"] == "2020"
    assert metadata["isbn"] == "1234567890123"
    assert metadata["publisher"] == "Example Publisher"
    assert metadata["categories"] == ["fiction", "adventure"]
    assert metadata["image_url"] == "http://image.url/thumb.jpg"


def test_parse_metadata_missing_fields():
    # Missing authors, categories, publishedDate, imageLinks
    item = {
        "volumeInfo": {
            "title": "Title Only",
            "industryIdentifiers": [],
            "publisher": ""
        }
    }
    with patch(
        'book_org.fetcher.extract_isbn_from_industry_ids',
        return_value=None
            ):
        metadata = fetcher.parse_metadata(item)
    assert metadata["title"] == "Title Only"
    assert metadata["authors"] == []
    assert metadata["published"] == ""
    assert metadata["isbn"] is None
    assert metadata["publisher"] == ""
    assert metadata["categories"] == ["uncategorized"]
    assert metadata["image_url"] is None


@patch('book_org.fetcher.requests.get')
def test_fetch_metadata_by_isbn_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [{"volumeInfo": {"title": "Book Title"}}]
    }
    mock_get.return_value = mock_response
    with patch(
        'book_org.fetcher.parse_metadata',
        return_value={"title": "Book Title"}
            ):
        result = fetcher.fetch_metadata_by_isbn("1234567890")
    assert result["title"] == "Book Title"


@patch('book_org.fetcher.requests.get')
def test_fetch_metadata_by_isbn_no_items(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"items": None}
    mock_get.return_value = mock_response
    result = fetcher.fetch_metadata_by_isbn("1234567890")
    assert result is None


@patch('book_org.fetcher.requests.get')
def test_fetch_metadata_by_isbn_bad_status(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response
    result = fetcher.fetch_metadata_by_isbn("1234567890")
    assert result is None


@patch('book_org.fetcher.requests.get')
def test_fetch_google_books_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [{"volumeInfo": {"title": "Some Book"}}]
    }
    mock_get.return_value = mock_response
    with patch(
        'book_org.fetcher.parse_metadata',
        return_value={"title": "Some Book"}
            ):
        result = fetcher.fetch_google_books("intitle:test")
    assert result["title"] == "Some Book"


@patch('book_org.fetcher.requests.get')
def test_fetch_google_books_no_items(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"items": None}
    mock_get.return_value = mock_response
    result = fetcher.fetch_google_books("intitle:test")
    assert result is None


@patch('book_org.fetcher.requests.get')
def test_fetch_google_books_exception(mock_get):
    mock_get.side_effect = Exception("Network error")
    result = fetcher.fetch_google_books("intitle:test")
    assert result is None


@patch('book_org.fetcher.fetch_google_books')
def test_fetch_metadata_by_title_author_noninteractive(mock_fetch):
    # Returns metadata for first 2 strategies, None for others
    mock_fetch.side_effect = [
        {"title": "Title A"},
        {"title": "Title B"},
        None,
        None,
    ]
    result = fetcher.fetch_metadata_by_title_author(
        "Author", "Title", interactive=False
        )
    # Non-interactive mode returns None even if metadata options found
    assert result is None


@patch('book_org.fetcher.fetch_google_books')
@patch('builtins.input', return_value="1")
@patch('book_org.fetcher.print_selection')
def test_fetch_metadata_by_title_author_interactive(
    mock_print,
    mock_input, mock_fetch
        ):
    mock_fetch.side_effect = [
        {"title": "Title A"},
        {"title": "Title B"},
        None,
        None,
    ]
    result = fetcher.fetch_metadata_by_title_author(
        "Author", "Title", interactive=True
        )
    assert result == {"title": "Title B"}
    mock_print.assert_called_once()


@patch('book_org.fetcher.requests.get')
def test_fetch_metadata_by_isbn_openlib_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [{"volumeInfo": {"title": "OpenLib Book"}}]
    }
    mock_get.return_value = mock_response
    with patch(
        'book_org.fetcher.parse_metadata',
        return_value={"title": "OpenLib Book"}
            ):
        result = fetcher.fetch_metadata_by_isbn_openlib("1234567890")
    assert result["title"] == "OpenLib Book"


@patch('book_org.fetcher.requests.get')
def test_fetch_metadata_by_isbn_openlib_no_items(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"items": None}
    mock_get.return_value = mock_response
    result = fetcher.fetch_metadata_by_isbn_openlib("1234567890")
    assert result is None


@patch('book_org.fetcher.requests.get')
def test_fetch_metadata_by_isbn_openlib_bad_status(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response
    result = fetcher.fetch_metadata_by_isbn_openlib("1234567890")
    assert result is None
