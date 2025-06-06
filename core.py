import os
import subprocess
from .Book import Book

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


def list_intersection_preserving_order(a, b):
    return [value for value in a if value in b]


# find all the categories defined in a list of books
# and group the similar ones together
def standardize_categories(list_of_books):
    for book in list_of_books:
        book.metadata.categories  # TODO iterate books and get their categories

    # TODO group categories together and standardize names


def log(action, text, noprint=False):
    if not noprint:
        print(action, text)

    with open("logfile.txt", "a+") as logfile:
        logfile.write(f"{action} {text}\n")


def link_file(src, dst):
    try:
        os.symlink(src, dst)
    except FileExistsError:
        pass


def move_book(i, save_to, dry=False):
    move = os.rename
    if dry:
        move = link_file

    if i.new_fullpath:
        # Move the book to the new path
        os.makedirs(i.new_path, exist_ok=True)
        log("[move]", f"'{i.fullpath}' => '{i.new_fullpath}'")
        move(i.fullpath, i.new_fullpath)

        # if the book corresponds to more than one category,
        # create a symlink on the other dirs
        if len(i.categories) > 1:
            for j in i.categories[1:]:
                newdir = os.path.join(save_to, "organized_books/", f"{j}"),
                os.makedirs(newdir, exist_ok=True)
                dir_to_link = os.path.join(newdir, i.new_filename)
                log("[link]", f"'{i.new_fullpath}' => '{dir_to_link}'")
                link_file(i.new_fullpath, dir_to_link)
    else:
        newdir = os.path.join(
            save_to,
            "organized_books",
            "no-metadata",
            i.filename
            )
        log("[move]", f"'{i.fullpath}' => '{newdir}'")
        move(i.fullpath, newdir)


def write_new_order_on_file(list_of_organized_books, save_to="."):
    no_metadata_dir = os.path.join(save_to, "organized_books", "no-metadata")
    uncateg_dir = os.path.join(save_to, "organized_books", "uncategorized")
    os.makedirs(no_metadata_dir, exist_ok=True)
    os.makedirs(uncateg_dir, exist_ok=True)

    for i in list_of_organized_books:
        move_book(i, save_to)


def progress_bar(full, fill):
    empty = full-fill

    factor = 50
    progress = "#"*int(fill/factor) + " "*int(empty/factor)

    percentage = 100*(fill/full)
    print(f"{percentage}%", progress)


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
