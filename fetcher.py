import requests
from .formatter import print_selection
from .config import GOOGLE_BOOKS_API, OPEN_LIBRARY_API
from .extractor import extract_isbn_from_industry_ids

# TODO Show image links in terminal
# (on the request its volumeInfo["imagelinks"]["thumbnail"])

# Dont just use the first item from the request
# TODO get more metadata from the file:
# either by making the program read the first pages
# or by allowing user input

# TODO let the user browse more of the request results


def parse_metadata(item):
    """Parses Google Books metadata."""
    volume_info = item.get("volumeInfo", {})
    return {
        "title": volume_info.get("title"),
        "authors": volume_info.get("authors", []),
        "published": volume_info.get("publishedDate", "")[:4],
        "isbn": extract_isbn_from_industry_ids(
            volume_info.get("industryIdentifiers", [])
            ),
        "publisher": volume_info.get("publisher", ""),
        "categories": [i.lower() for i in volume_info.get(
            "categories", ["uncategorized"]
            )],
        "image_url": volume_info.get("imageLinks", {}).get("thumbnail")
    }


def fetch_metadata_by_isbn(isbn):
    """Fetches metadata using ISBN."""
    url = f"{GOOGLE_BOOKS_API}isbn:{isbn}"
    response = requests.get(url)
    if response.status_code == 200:
        items = response.json().get("items")
        if items:
            return parse_metadata(items[0])
    return None


def fetch_google_books(query: str):
    """Helper to query the Google Books API and return parsed results."""
    url = f"{GOOGLE_BOOKS_API}{query}"
    # logger.debug(f"Querying Google Books API: {url}")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            items = response.json().get("items")
            if items:
                return parse_metadata(items[0])
    except Exception:
        pass
        # logger.warning(f"Failed to fetch metadata from API: {e}")
    return None


SEARCH_PATTERNS = [
    lambda a, t: f"intitle:{t}+inauthor:{a}",  # normal
    lambda a, t: f"intitle:{a}+inauthor:{t}",  # reversed
    lambda a, t: f"intitle:{t}",               # just title
    lambda a, t: f"intitle:{a}"                # just author
]


def fetch_metadata_by_title_author(
    author: str,
    title: str,
    interactive=False,
    filename=""
):
    """Attempts many strategies to fetch metadata using author and title."""

    metadata_options = []

    for strategy in SEARCH_PATTERNS:
        query = strategy(author, title)
        # logger.info(f"Trying search query: {query}")
        metadata = fetch_google_books(query)
        if metadata:
            metadata_options.append(metadata)

    if interactive and metadata_options:
        print_selection(metadata_options)
        selection = input(
            "Select which metadata is correct [0-n], enter to skip: "
            )
        if selection.isdigit():
            index = int(selection)
            if 0 <= index < len(metadata_options):
                return metadata_options[index]

    # logger.warning("No metadata found.")
    return None


def fetch_metadata_by_isbn_openlib(isbn):
    """Fetches metadata using ISBN."""
    url = f"{OPEN_LIBRARY_API}isbn={isbn}"
    response = requests.get(url)
    if response.status_code == 200:
        items = response.json().get("items")
        if items:
            return parse_metadata(items[0])
    return None
