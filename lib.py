import re
import requests
import os
from formatter import beautifulprint
from config import GOOGLE_BOOKS_API
from extractor import extract_series, extract_isbn_from_filename, extract_isbn_from_industry_ids
from parser import parse_filename


def check_author_in_filename(authors, title):
    title = title.lower()

    author_words = []
    for author in authors:
        author_words += author.replace(",", "").split()

    author_words = [word.lower() for word in author_words if len(word) >= 3]

    return any(word in title for word in author_words)


def fetch_metadata_by_isbn(isbn):
    """Fetches metadata using ISBN."""
    url = f"{GOOGLE_BOOKS_API}isbn:{isbn}"
    response = requests.get(url)
    if response.status_code == 200:
        items = response.json().get("items")
        if items:
            return parse_metadata(items[0])
    return None


def fetch_metadata_by_title_author(author, title, interactive=False):
    """Fetches metadata using title and author."""

    metadata_result = {}

    if interactive: metadata_options = []

    print(f"trying search: title:{title} author:{author}")
    query = f'intitle:{title}+inauthor:{author}'
    url = f"{GOOGLE_BOOKS_API}{query}"
    response = requests.get(url)

    if response.status_code == 200:
        items = response.json().get("items")
        if items:
            return parse_metadata(items[0])

    if not metadata_result and author and title:
        print(f"trying search: title:{author} author:{title}")
        # check if author and title are reversed
        query = f'intitle:{author}+inauthor:{title}'
        url = f"{GOOGLE_BOOKS_API}{query}"
        response = requests.get(url)

        if response.status_code == 200:
            items = response.json().get("items")
            if items:
                metadata_result= parse_metadata(items[0])
                if interactive: metadata_options.append(metadata_result)

        if check_author_in_filename(metadata_result.get("authors", []), title):
            return metadata_result

    if not metadata_result and title:
        print(f"trying search: title:{title}")
        # check only title
        query = f'intitle:{title}'
        url = f"{GOOGLE_BOOKS_API}{query}"
        response = requests.get(url)

        if response.status_code == 200:
            items = response.json().get("items")
            if items:
                metadata_result= parse_metadata(items[0])
                if interactive: metadata_options.append(metadata_result)

        if check_author_in_filename(metadata_result.get("authors", []), title):
            return metadata_result


    if not metadata_result and author:
        print(f"trying search: title:{author}")
        # check only author
        query = f'intitle:{author}'
        url = f"{GOOGLE_BOOKS_API}{query}"
        response = requests.get(url)

        if response.status_code == 200:
            items = response.json().get("items")
            if items:
                metadata_result= parse_metadata(items[0])
                if interactive: metadata_options.append(metadata_result)

        if check_author_in_filename(metadata_result.get("authors", []), title):
            return metadata_result

    if interactive and metadata_options:
        beautifulprint(metadata_options)
        metadata_selection = input("Select which metadata is right, enter for none: ")
        if metadata_selection.isdigit() and int(metadata_selection) < 3:
            return metadata_options[int(metadata_selection)]

    print("nothing was found")
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


def parse_metadata(item):
    """Parses Google Books metadata."""
    volume_info = item.get("volumeInfo", {})
    print(volume_info.get("title"), volume_info.get("categories", ["uncategorized"]))
    print("FOUND TITLE", volume_info.get("title", ""))
    print("FOUND AUTHORS", volume_info.get("authors", []))
    return {
        "title": volume_info.get("title"),
        "authors": volume_info.get("authors", []),
        "published": volume_info.get("publishedDate", "")[:4],
        "isbn": extract_isbn_from_industry_ids(volume_info.get("industryIdentifiers", [])),
        "publisher": volume_info.get("publisher", ""),
        "categories": [i.lower() for i in volume_info.get("categories", ["uncategorized"])]
    }


def main(file_path, interactive=False):
    print(f"\nProcessing: {file_path}")
    isbn = extract_isbn_from_filename(file_path)
    metadata = None
    if isbn:
        print(f"Found ISBN: {isbn}")
        metadata = fetch_metadata_by_isbn(isbn)
    else:
        filename = os.path.splitext(os.path.basename(file_path))[0]
        parsed_filename = parse_filename(filename)
        author, title = parsed_filename.get("authors", ""), parsed_filename.get("title", "").replace("_ ", ": ").replace("_", " ")
        if title:
            print(f"No ISBN found. Using title/author fallback: {title} by {author}")
            metadata = fetch_metadata_by_title_author(author, title, interactive)

    if metadata:
        print("Metadata fetched:")
        for k, v in metadata.items():
            pass
            print(f"  {k.capitalize()}: {v}")
    else:
        print("=================")
        print(file_path)
        print(file_name)
        print("No metadata found.")
        print("=================")

    return metadata

def category_fallback(filename):
    categories = []

    if ("comp" in filename or " hack" in filename or " cyber" in filename or " vpn "
        in filename):
        categories.append("computers")


    if ("aero" in filename or " aircr"
        in filename or "flight" in filename):
        categories.append("aeronautics")


    if ("astron" in filename or ("star" in filename and not "started" in filename) or
        "galaxy" in filename or "planet" in filename or
        "moon" in filename):
        categories.append("astronomy")


    if "phys" in filename or "fisica" in filename:
        categories.append("physics")


    if "animal" in filename:
        categories.append("zoology")


    if ("army" in filename or " war " in filename
         or " milit" in filename):
        categories.append("military")


    if "anatom" in filename:
        categories.append("anatomy")


    if (" anim" in filename or " draw" in filename or " paint"
        in filename):
        categories.append("art")


    if "german" in filename:
        categories.append("german")


    if ("game" in filename or "unity" in filename or "godot"
        in filename):
        categories.append("games")


    if ("training" in filename or "excercise" in filename or "martial"
        in filename):
        categories.append("training")

    if ("engineering" in filename):
        categories.append("engineering")

    return categories


# Example usage
if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=str)
    parser.add_argument("-r", "--recursive", type=bool)

    args = parser.parse_args()


    if os.path.isfile(args.directory):
        print(main(args.directory))

    elif os.path.isdir(args.directory):
        for i in os.listdir(args.directory):
            if os.path.isfile(os.path.join(args.directory,i)):
                main(i)

