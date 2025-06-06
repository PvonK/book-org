import os
import subprocess
from .Book import Book
from .formatter import progress_bar
from .file_sorter import move_book


# TODO interactive renamer and author input for when there is a total miss
# Also a query editor in case the user wants to manually query the metadata
# (or the metadata found gets close but not quite) like:


def find_find_all_files(find_dir):
    result = subprocess.run(
        ['find', find_dir, '-type', 'f'],
        stdout=subprocess.PIPE)
    result = result.stdout.decode("utf-8").split('\n')
    result.pop()
    return result


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


def organize_dir(directory, output=".", dry=False, interactive=False):
    if os.path.isfile(directory):
        book = Book(directory, interactive_organizer=interactive)
        book.organize_book()
        return book

    all_files = find_find_all_files(directory)
    # all_books = []
    for n in range(len(all_files)):
        file = all_files[n]
        if os.path.isfile(file):
            ext = os.path.splitext(file)[1]
            if not is_ext_valid(ext):
                continue
            book = Book(file, interactive_organizer=interactive)
            book.organize_book()
            # all_books.append(book.filename)
            move_book(book, output, dry)
        progress_bar(len(all_files), n)

    # nlp_categorizer.main(all_books)
