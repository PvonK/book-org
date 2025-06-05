import re
import requests
import os
from pathlib import Path
from .formatter import beautifulprint
from .config import GOOGLE_BOOKS_API


def check_author_in_filename(authors, title):
    title = title.lower()
    
    author_words = []
    for author in authors:
        author_words += author.replace(",", "").split()

    author_words = [word.lower() for word in author_words if len(word) >= 3]

    return any(word in title for word in author_words)

def extract_series(name):
    series_match = re.match(r'[\[\(]([^\]\)]+)[\]\)]\s*(.+)', name)
    if series_match:
        return series_match.groups()


def extract_year(name):
    pub_year_match = re.search(r'\((\d{4}),\s*([^)]+)\)', name)
    if pub_year_match:
        year = pub_year_match.group(1)
        publisher = pub_year_match.group(2).strip()
        name = name[:pub_year_match.start()].strip()            
        return year, publisher, name


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
        match_year = extract_year(title)
        if match_year:
            result['year'], result['publisher'], title = match_year

        return author.strip(), title.strip()
    
    print("failed to find authors on book:", filename)
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

def extract_isbn_from_industry_ids(identifiers):
    for id_obj in identifiers:
        if "ISBN_13" in id_obj.get("type", ""):
            return id_obj.get("identifier")
    return ""

def main(file_path, interactive=False):
    print(f"\nProcessing: {file_path}")
    isbn = extract_isbn_from_filename(file_path)
    metadata = None
    if isbn:
        print(f"Found ISBN: {isbn}")
        metadata = fetch_metadata_by_isbn(isbn)
    else:
        author, title = extract_title_author_from_filename(file_path)
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
        print("No metadata found.")

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
    series_match = extract_series(name)
    if series_match:
        result['series'], name = series_match


    # 4. Extract year + publisher (e.g. (2001, Wiley))
    match_year = extract_year(name)
    if match_year:
        result['year'], result['publisher'], name = match_year

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

        if title_part.count("-") > 3:
            title_part = title_part.replace("-", " ")
        # This here is to separate the publisher from the title
        # I only do it here, when authors are separated, because i feel
        # like only the ones with correctly formated author names would also have publishing data  
        elif title_part.count("-") > 0:
            title_part = "-".join(title_part.split("-",-2)[:-1])

        result['title'] = title_part.strip()
        result['authors'] = people_part.strip()

    elif " by " in name:
        if title_part.count("-") > 3:
            title_part = title_part.replace("-", " ")
        elif title_part.count("-") > 0:
            title_part = "-".join(title_part.split("-",-2)[:-1])

        title_part, people_part = name.split(' by ', 1)


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

