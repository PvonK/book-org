# core.py

import os
from .Book import Book
from .formatter import progress_bar
from .file_sorter import move_book


# TODO interactive renamer and author input for when there is a total miss
# Also a query editor in case the user wants to manually query the metadata
# (or the metadata found gets close but not quite) like:


def find_all_files(find_dir):
    all_files = []
    for dirpath, _, filenames in os.walk(find_dir):
        for file in filenames:
            full_path = os.path.join(dirpath, file)
            all_files.append(full_path)
    return all_files


# find all the categories defined in a list of books
# and group the similar ones together
def standardize_categories(list_of_books):
    for book in list_of_books:
        book.metadata.categories  # TODO iterate books and get their categories

    # TODO group categories together and standardize names


def is_ext_valid(ext):
    valid_ext = [
        ".mobi",
        ".djvu",
        ".txt",
        ".epub",
        ".pdf",
    ]
    return ext in valid_ext


def organize_dir(
    directory,
    output=".",
    dry=False,
    interactive=False,
    output_path_dir=None
        ):
    if os.path.isfile(directory):
        book = Book(
            directory,
            interactive_organizer=interactive,
            output_path_dir=output_path_dir
            )
        book.organize_book()
        return book

    all_files = find_all_files(directory)
    for n in range(len(all_files)):
        file = all_files[n]
        if os.path.isfile(file):

            ext = os.path.splitext(file)[1]
            if not is_ext_valid(ext):
                continue

            book = Book(
                file,
                interactive_organizer=interactive,
                output_path_dir=output_path_dir
                )
            book.organize_book()
            move_book(book, dry)

        progress_bar(len(all_files), n)
