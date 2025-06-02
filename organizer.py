import os
import argparse
import subprocess
import lib
from unidecode import unidecode
#import nlp_categorizer
from colorama import Fore, Back, Style

# TODO why would i need this? i dont need to detct if a book is already renamed
pattern = r"""
^
(?P<authors>[^-\[\]()]+)
(?: - \[(?P<series>[^\]]+)\])?
 - (?P<title>[^()\[\]]+)
(?: \((?P<year>\d{4})\))?
 \[(?P<isbn>[\d\-]+)\]
\.(?P<ext>\w+)
$
"""




def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=str)
    parser.add_argument("-o", "--output", type=str)
    parser.add_argument("-r", "--recursive", type=bool)

    args = parser.parse_args()

    return args


def find_find_all_files(find_dir):
    result = subprocess.run(['find', find_dir, '-type', 'f'], stdout=subprocess.PIPE)
    result = result.stdout.decode("utf-8").split('\n')
    result.pop()
    return result

def list_intersection_preserving_order(a,b):
    return [value for value in a if value in b]

class Book():
    def __init__(self, path_to_file):
        self.path, self.filename = os.path.split(path_to_file)
        self.fullpath = path_to_file
        self.metadata : dict = {}
        self.isbn : int = 0
        self.categories = ["no-metadata"]
        self.new_filename = ""
        self.new_path = ""
        self.new_fullpath = ""


    def organize_book(self):
        self.find_metadata()
        self.set_new_filename(self.metadata)
        self.set_categories()
        self.set_new_path()

    # Searches for the books metadata on different information clients
    def find_metadata(self):
        self.metadata = lib.main(self.fullpath)

    # Renames the book based on the newly aquired metadata
    def set_new_filename(self, metadata):
        if not metadata:
            self.new_filename=self.filename
            return

        authors = ", ".join(metadata.get("authors", [])).replace("/", "_")
        if authors: authors += " - "
        title = metadata.get("title").replace("/", "_")
        published = metadata.get("published","").replace("/", "_")
        if published: published = f" ({published})"
        isbn = metadata.get("isbn").replace("/", "_")
        if isbn: isbn = f" [{isbn}]"
        ext = os.path.splitext(self.filename)[1]

        self.new_filename = f"{authors}{title}{published}{isbn}{ext}"

    # Finds the categories the book belongs to and orders them according to their priority
    def set_categories(self):
        if self.metadata:
            self.categories = self.metadata.get("categories", ["uncategorized"])

            self.categories += lib.category_fallback(unidecode(self.metadata.get("title","").lower()))

        else:
            self.categories = ["no-metadata"]

            self.categories += lib.category_fallback(unidecode(self.new_filename.lower()))

        if len(self.categories) > 1:
            if "no-metadata" in self.categories:
                self.categories.remove("no-metadata")
            elif "uncategorized" in self.categories:
                self.categories.remove("uncategorized")

    # change the path of the book based on the categories
    def set_new_path(self, pre_defined_categories=[]):
        if pre_defined_categories:
            categories_to_go_on = list_intersection_preserving_order(self.categories, pre_defined_categories)
        else:
            categories_to_go_on = self.categories

        self.new_path = os.path.join("organized_books/",f"{categories_to_go_on[0]}")

        if self.new_filename:
            self.new_fullpath = os.path.join(self.new_path,self.new_filename)


# find all the categories defined in a list of books and group the similar ones together
def standardize_categories(list_of_books):
    for book in list_of_books:
        book.metadata.categories # TODO iterate books and get their categories
    
    # TODO group categories together and standardize names

def log(action, text, color=Style.RESET_ALL, noprint=False):
    if not noprint: print(color+action, text)
    if not noprint: print(Style.RESET_ALL)
    with open("logfile.txt", "a+") as logfile:
        logfile.write(f"{action} {text}\n")


def move_book(i, save_to):
    if i.new_fullpath:
        # Move the book to the new path
        os.makedirs(i.new_path, exist_ok=True)
        log("[move]", f"'{i.fullpath}' => '{i.new_fullpath}'", Fore.GREEN)
        os.rename(i.fullpath, i.new_fullpath)

        # if the book corresponds to more than one category, create a symlink on the other dirs
        if len(i.categories) > 1:
            for j in i.categories[1:]:
                os.makedirs(os.path.join(save_to,"organized_books/",f"{j}"), exist_ok=True)
                dir_to_link = os.path.join(save_to,"organized_books/",f"{j}", i.new_filename)
                log("[link]", f"'{i.new_fullpath}' => '{dir_to_link}'")
                try:
                    os.symlink(i.new_fullpath, dir_to_link)
                except FileExistsError:
                    pass
    else:
        newdir = os.path.join(save_to,"organized_books","no-metadata", i.filename)
        log(f"[move]", f"'{i.fullpath}' => '{newdir}'", Fore.RED)
        os.rename(i.fullpath, newdir)


def write_new_order_on_file(list_of_organized_books, save_to="."):
    os.makedirs(os.path.join(save_to,"organized_books","no-metadata"), exist_ok=True)
    os.makedirs(os.path.join(save_to,"organized_books","uncategorized"), exist_ok=True)

    with open("run_commands_to_move", "a+") as logfile:

        for i in list_of_organized_books:
            move_book(i, save_to)



def progress_bar(full, fill):
    empty = full-fill

    factor = 50
    progress = "#"*int(fill/factor) + " "*int(empty/factor)

    print(progress)


def organize_dir(directory, output="."):
    if os.path.isfile(directory):
        return Book(directory)

    all_files = find_find_all_files(directory)
    #all_books = []
    for n in range(len(all_files)):
        file = all_files[n]
        if os.path.isfile(file):
            book = Book(file)
            book.organize_book()
            #all_books.append(book.filename)
            move_book(book, output)
        progress_bar(len(all_files), n)

    #nlp_categorizer.main(all_books)


if __name__=="__main__":

    args = parse_args()
    r = organize_dir(args.directory)

