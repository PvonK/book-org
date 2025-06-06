import os


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
