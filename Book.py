# Book.py

import os
from unidecode import unidecode
from .fetcher import fetch_metadata_by_isbn
from .fetcher import fetch_metadata_by_title_author
from .extractor import extract_isbn_from_filename, extract_file_extension
from .parser import parse_filename
from .formatter import log
from .categorizer import category_fallback
from book_org.embedded_metadata import extract_metadata as\
    extract_embedded_metadata


class Book():
    def __init__(
        self,
        path_to_file,
        interactive_organizer=False,
        output_path_dir=None
            ):
        self.path, self.filename = os.path.split(path_to_file)
        self.fullpath = path_to_file
        self.metadata: dict = {}
        self.isbn: int = 0
        self.categories = ["no-metadata"]
        self.new_filename = ""
        self.new_path = ""
        self.new_fullpath = ""
        self.output_path_dir = output_path_dir or "organized_books"
        self.interactive_organizer = interactive_organizer

    def organize_book(self):
        self.find_metadata()
        self.set_new_filename(self.metadata)
        self.set_categories()
        self.set_new_path()

    def find_metadata(self):
        embedded_meta = extract_embedded_metadata(self.fullpath)

        if not embedded_meta.get("isbn"):
            embedded_meta["isbn"] = extract_isbn_from_filename(self.filename)

        if all(embedded_meta.values()):
            log("[INFO]", "Using embedded metadata.")
            self.metadata = embedded_meta
            return embedded_meta

        if embedded_meta.get("isbn"):
            log("[INFO]", "Fetching metadata via embedded ISBN.")
            self.metadata = fetch_metadata_by_isbn(embedded_meta["isbn"])
            return self.metadata

        # Fall back to filename parsing
        parsed = parse_filename(self.filename)
        author = embedded_meta.get("author") or parsed.get("authors", "")
        title = embedded_meta.get("title") or parsed.get("title", "")
        title = title.replace("_ ", ": ").replace("_", " ")

        if author and title:
            log("[INFO]", f"Fallback to title/author: '{title}' by '{author}'")
            self.metadata = fetch_metadata_by_title_author(
                author, title,
                interactive=self.interactive_organizer,
                filename=self.filename
            )
            return self.metadata

        log("[WARNING]", "Only partial metadata found.")
        self.metadata = embedded_meta
        return self.metadata

    # Renames the book based on the newly aquired metadata
    def set_new_filename(self, metadata):
        if not metadata:
            name, ext = extract_file_extension(self.filename)
            name = name.replace("_ ", ": ").replace("/", "_")
            self.new_filename = f"{name}{ext}"
            return

        authorslist = metadata.get("authors", [])
        if len(metadata.get("authors", [])) > 3:
            authorslist = metadata.get("authors", [])[:2]

        authors = ", ".join(authorslist).replace("/", "_")
        if authors:
            authors += " - "

        title = metadata.get("title").replace("/", "_")

        published = metadata.get("published", "").replace("/", "_")
        if published:
            published = f" ({published})"

        isbn = metadata.get("isbn").replace("/", "_")
        if isbn:
            isbn = f" [{isbn}]"

        ext = extract_file_extension(self.filename)[1]

        self.new_filename = f"{authors}{title}{published}{isbn}{ext}"

    # Finds the categories the book belongs to
    def set_categories(self):
        self.categories = []

        categories = self.metadata.get(
            "categories", []) if self.metadata else []

        if categories:
            self.categories = categories
        else:
            title = self.metadata.get("title", "") if self.metadata else ""
            fallback = category_fallback(unidecode(title.lower()))
            if fallback:
                self.categories = fallback
            elif self.metadata:
                self.categories = ["uncategorized"]

        if not self.metadata:
            self.categories = ["no-metadata"] + self.categories

    # change the path of the book based on the categories
    def set_new_path(self, pre_defined_categories=[]):
        if pre_defined_categories:
            categories_to_go_on = [
                value for value in self.categories
                if value in pre_defined_categories
                ]
        else:
            categories_to_go_on = self.categories

        self.new_path = os.path.join(
            self.output_path_dir,
            f"{categories_to_go_on[0]}"
            )

        if self.new_filename:
            self.new_fullpath = os.path.join(self.new_path, self.new_filename)
