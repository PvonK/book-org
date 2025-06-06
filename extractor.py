# extractor.py

""" Data extractors from filename """
import re


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


def extract_isbn_from_industry_ids(identifiers):
    for id_obj in identifiers:
        if "ISBN_13" in id_obj.get("type", ""):
            return id_obj.get("identifier")
    return ""
