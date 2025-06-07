# extractor.py

""" Data extractors from filename """
import re
from .config import valid_file_extensions


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
    match = re.search(r'(?:97[89])?\d{9}[\dXx]\b', filename)
    return match.group(0) if match else None


def extract_isbn_from_industry_ids(identifiers):
    for id_obj in identifiers:
        if "ISBN_13" in id_obj.get("type", ""):
            return id_obj.get("identifier")
    return ""


def check_author_in_filename(authors, title):
    title = title.lower()
    # extract words with 3+ characters
    title_words = set(re.findall(r'\b\w{3,}\b', title))

    for author in authors:
        if not author:
            continue
        # Normalize and split author name
        author_words = re.findall(r'\b\w{3,}\b', author.lower())
        if any(word in title_words for word in author_words):
            return True
    return False


def extract_file_extension(filename):
    for i in valid_file_extensions:
        if filename.endswith(i):
            return filename.rsplit(i, 1)[0], i
