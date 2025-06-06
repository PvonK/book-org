# file_sorter.py

import os
from .formatter import log


def link_file(src, dst):
    try:
        os.symlink(src, dst)
    except FileExistsError:
        pass


def move_book(i, dry=False):
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
                newdir = os.path.join(i.output_path_dir, f"{j}")
                os.makedirs(newdir, exist_ok=True)
                dir_to_link = os.path.join(newdir, i.new_filename)
                log("[link]", f"'{i.new_fullpath}' => '{dir_to_link}'")
                link_file(i.new_fullpath, dir_to_link)
    else:
        newdir = os.path.join(i.output_path_dir, "no-metadata")
        os.makedirs(newdir, exist_ok=True)
        new_path = os.path.join(i.output_path_dir, "no-metadata", i.filename)
        log("[move]", f"'{i.fullpath}' => '{new_path}'")
        move(i.fullpath, new_path)
