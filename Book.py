import os
from unidecode import unidecode
from .lib import lib_main, category_fallback


class Book():
    def __init__(self, path_to_file, interactive_organizer=False):
        self.path, self.filename = os.path.split(path_to_file)
        self.fullpath = path_to_file
        self.metadata: dict = {}
        self.isbn: int = 0
        self.categories = ["no-metadata"]
        self.new_filename = ""
        self.new_path = ""
        self.new_fullpath = ""
        self.interactive_organizer = interactive_organizer

    def organize_book(self):
        self.find_metadata()
        self.set_new_filename(self.metadata)
        self.set_categories()
        self.set_new_path()

    # Searches for the books metadata on different information clients
    def find_metadata(self):
        self.metadata = lib_main(self.filename, self.interactive_organizer)

    # Renames the book based on the newly aquired metadata
    def set_new_filename(self, metadata):
        if not metadata:
            self.new_filename = self.filename.replace("_ ", ": ")
            self.new_filename = self.filename.replace("/", "_")
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
            categories_to_go_on = list_intersection_preserving_order(
                self.categories, pre_defined_categories
                )
        else:
            categories_to_go_on = self.categories

        self.new_path = os.path.join(
            "organized_books/",
            f"{categories_to_go_on[0]}"
            )

        if self.new_filename:
            self.new_fullpath = os.path.join(self.new_path, self.new_filename)
