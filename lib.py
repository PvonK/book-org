import re
import requests
import os
from pathlib import Path


GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes?q="
OPEN_LIBRARY_API = "https://openlibrary.org/search.json?"


def extract_isbn_from_filename(filename):
    """Extracts ISBN-10 or ISBN-13 from filename."""
    match = re.search(r'\b(?:97[89])?\d{9}[\dXx]\b', filename)
    return match.group(0) if match else None

def extract_title_author_from_filename(filename):
    """Very naive guess of title and author from filename structure like 'Author - Title.ext'."""
    base = os.path.splitext(os.path.basename(filename))[0]
    data = parse_filename(base)
    return data.get("authors", ""), data.get("title", "").replace("_ ", ": ").replace("_", " ")

    if '-' in base:
        author, title = base.split('-', 1)
        title = title.replace("_ ", ": ").replace("_", " ")
        title = title.split("-")[0] # benchamrk if this is a good change or not, sometimes its part of the title, sometimes its not
        return author.strip(), title.strip()
    return None, None

def fetch_metadata_by_isbn(isbn):
    """Fetches metadata using ISBN."""
    url = f"{GOOGLE_BOOKS_API}isbn:{isbn}"
    response = requests.get(url)
    if response.status_code == 200:
        items = response.json().get("items")
        if items:
            return parse_metadata(items[0])
    return None


def fetch_metadata_by_title_author(author, title):
    """Fetches metadata using title and author."""
    query = f'intitle:{title}+inauthor:{author}' if author else f'intitle:{title}'
    url = f"{GOOGLE_BOOKS_API}{query}"
    response = requests.get(url)
    if response.status_code == 200:
        items = response.json().get("items")
        if items:
            return parse_metadata(items[0])
    # try only the title
    fetch_metadata_by_title_author(None, title)
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


def fetch_metadata_by_title_author(author, title):
    """Fetches metadata using title and author."""
    query = f'title={title}&author={author}' if author else f'title={title}'
    url = f"{OPEN_LIBRARY_API}{query}"
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
    return {
        "title": volume_info.get("title"),
        "authors": volume_info.get("authors", []),
        "published": volume_info.get("publishedDate", "")[:4],
        "isbn": extract_isbn_from_industry_ids(volume_info.get("industryIdentifiers", [])),
        "publisher": volume_info.get("publisher", ""),
        "categories": [i.lower() for i in volume_info.get("categories", ["uncategorized"])]
    }

def extract_isbn_from_industry_ids(identifiers):
    for id_obj in identifiers:
        if "ISBN_13" in id_obj.get("type", ""):
            return id_obj.get("identifier")
    return ""

def main(file_path):
    if __name__ == "__main__": print(f"\nProcessing: {file_path}")
    isbn = extract_isbn_from_filename(file_path)
    metadata = None
    if isbn:
        if __name__ == "__main__": print(f"Found ISBN: {isbn}")
        metadata = fetch_metadata_by_isbn(isbn)
    else:
        author, title = extract_title_author_from_filename(file_path)
        if title: 
            if __name__ == "__main__": print(f"No ISBN found. Using title/author fallback: {title} by {author}")
            metadata = fetch_metadata_by_title_author(author, title)

    if metadata:
        if __name__ == "__main__": print("Metadata fetched:")
        for k, v in metadata.items():
            pass
            if __name__ == "__main__": print(f"  {k.capitalize()}: {v}")
    else:
        if __name__ == "__main__": print("=================")
        if __name__ == "__main__": print(file_path)
        if __name__ == "__main__": print("No metadata found.")

    return metadata





def clean_filename(name):
    name = name.replace('_ ', ':')
    name = name.replace('_', ' ')
    name = name.replace('–', '-')
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def parse_annas_filename(filename):
    #OSINT_ Open Source Intelligence -- Victor Bancayan -- Edicion Especial, 2023 -- Hack Underway -- 685c26d72a0b6da440aa5db5f2b28386 -- Anna’s Archive.pdf
    os.path.splitext(filename)[1]
    title,authors=filename.split(" -- ", 3)[:2]
    return {"title":title, "authors":authors}


def parse_filename(filename):
    if "Anna’s Archive" in filename: return parse_annas_filename(filename)

    result = {
        'series': None,
        'authors': None,
        'editors': None,
        'title': None,
        'publisher': None,
        'year': None,
        'volume': None,
        'extension': None,
    }

    # 1. Remove extension
    path = Path(filename)
    result['extension'] = path.suffix.replace('.', '')
    name = path.stem

    # 2. Clean up and normalize
    name = clean_filename(name)

    # 3. Extract bracketed or parenthetical series
    series_match = re.match(r'[\[\(]([^\]\)]+)[\]\)]\s*(.+)', name)
    if series_match:
        result['series'], name = series_match.groups()

    # 4. Extract year + publisher (e.g. (2001, Wiley))
    pub_year_match = re.search(r'\((\d{4}),\s*([^)]+)\)', name)
    if pub_year_match:
        result['year'] = pub_year_match.group(1)
        result['publisher'] = pub_year_match.group(2).strip()
        name = name[:pub_year_match.start()].strip()

    # 5. Handle year-only case
    elif re.search(r'\((\d{4})\)$', name):
        result['year'] = re.search(r'\((\d{4})\)$', name).group(1)
        name = re.sub(r'\((\d{4})\)$', '', name).strip()

    # 6. Remove trailing junk (e.g., z-lib, libgen)
    name = re.sub(r'-?for\(z-lib.*?\)', '', name).strip()
    name = re.sub(r'-?libgen.*$', '', name).strip()

    # 7. Split authors and title (use ` - ` delimiter)
    if ' - ' in name:
        people_part, title_part = name.split(' - ', 1)
        result['title'] = title_part.strip()
        result['authors'] = people_part.strip()
    else:
        # Fallback: title only
        result['title'] = name.strip()

    # 8. Check for volume in title
    volume_match = re.search(r'(Volume|V\.)\s*(\d+)', result['title'] or '')
    if volume_match:
        result['volume'] = volume_match.group(2)

    return result

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

    return categories


# Example usage
if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=str)
    parser.add_argument("-r", "--recursive", type=bool)

    args = parser.parse_args()


    if os.path.isfile(args.directory):
        main(args.directory)

    elif os.path.isdir(args.directory):
        for i in os.listdir(args.directory):
            if os.path.isfile(os.path.join(args.directory,i)):
                main(i)

