# Book.py

import os
from unidecode import unidecode
from .fetcher import fetch_metadata_by_isbn
from .fetcher import fetch_metadata_by_title_author
from .extractor import extract_isbn_from_filename
from .parser import parse_filename
from .formatter import log


def category_fallback(filename):
    categories = []

    if (
         "comp" in filename or
         " hack" in filename or
         " cyber" in filename or
         " vpn " in filename):
        categories.append("computers")

    if (
         "aero" in filename or
         " aircr" in filename or
         "flight" in filename):
        categories.append("aeronautics")

    if (
         "astron" in filename or
         ("star" in filename and "started" not in filename) or
         "galaxy" in filename or
         "planet" in filename or
         "moon" in filename
         ):
        categories.append("astronomy")

    if "phys" in filename or "fisica" in filename:
        categories.append("physics")

    if "animal" in filename:
        categories.append("zoology")

    if (
         "army" in filename or
         " war " in filename or
         " milit" in filename):
        categories.append("military")

    if "anatom" in filename:
        categories.append("anatomy")

    if (
         " anim" in filename or
         " draw" in filename or
         " paint" in filename):
        categories.append("art")

    if "german" in filename:
        categories.append("german")

    if (
         "game" in filename or
         "unity" in filename or
         "godot" in filename):
        categories.append("games")

    if (
         "training" in filename or
         "excercise" in filename or
         "martial" in filename):
        categories.append("training")

    if ("engineering" in filename):
        categories.append("engineering")

    return categories


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

    # Searches for the books metadata on different information clients
    def find_metadata(self):
        log("[SEPARATOR]", "=")
        log("[INFO]", f"Processing: {self.filename}")
        isbn = extract_isbn_from_filename(self.filename)
        metadata = None

        if isbn:
            log("[INFO]", f"Found ISBN in filename: {isbn}")
            try:
                metadata = fetch_metadata_by_isbn(isbn)
                if metadata:
                    log("[SUCCESS]", "Successfully fetched metadata via ISBN.")
                else:
                    log("[WARNING]", "No metadata found with extracted ISBN.")
            except Exception as e:
                log("[ERROR]", f"Exception during ISBN fetch: {e}")
        else:
            filename = os.path.splitext(os.path.basename(self.filename))[0]
            parsed_filename = parse_filename(filename)
            author = parsed_filename.get("authors", "")
            title = parsed_filename.get("title", "")
            title = title.replace("_ ", ": ").replace("_", " ")

            if not title:
                log(
                    "[WARNING]",
                    "No ISBN or usable title extracted from filename."
                    )
            else:
                log(
                    "[INFO]",
                    f"No ISBN found. \
                        Trying title/author: '{title}' by '{author}'"
                    )
                try:
                    metadata = fetch_metadata_by_title_author(
                        author,
                        title,
                        interactive=self.interactive_organizer,
                        filename=self.filename
                    )
                    if metadata:
                        log(
                            "[SUCCESS]",
                            "Successfully fetched metadata via title/author."
                            )
                    else:
                        log(
                            "[WARNING]",
                            "No metadata found with title/author fallback."
                            )
                except Exception as e:
                    log("[ERROR]", f"Exception during title/author fetch: {e}")

        if metadata:
            log("[INFO]", "Metadata fetched successfully:")
            for k, v in metadata.items():
                log("[DATA]", f"{k.capitalize()}: {v}")
        else:
            log("[FAILURE]", f"Failed to find metadata for: {self.filename}")

        self.metadata = metadata

    # Renames the book based on the newly aquired metadata
    def set_new_filename(self, metadata):
        if not metadata:
            name, ext = os.path.splitext(self.filename)
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

        ext = os.path.splitext(self.filename)[1]

        self.new_filename = f"{authors}{title}{published}{isbn}{ext}"

    # Finds the categories the book belongs to
    # and orders them according to their priority
    def set_categories(self):
        if self.metadata:
            self.categories = self.metadata.get(
                "categories", ["uncategorized"]
                )

            if "uncategorized" in self.categories:
                self.categories += category_fallback(
                    unidecode(self.metadata.get("title", "").lower())
                    )

        else:
            self.categories += category_fallback(
                unidecode(self.new_filename.lower())
                )
            if not self.categories:
                self.categories = ["no-metadata"]

        if len(self.categories) > 1:
            if "no-metadata" in self.categories:
                self.categories.remove("no-metadata")
            elif "uncategorized" in self.categories:
                self.categories.remove("uncategorized")

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
