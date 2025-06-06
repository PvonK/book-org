# formatter.py

import subprocess
import requests
import os

try:
    term_size = os.get_terminal_size()
    columns = term_size.columns
    lines = term_size.lines
except OSError:
    term_size = None
    columns = 0
    lines = 0


def download_image(url, path="/tmp/cover.jpg"):
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, "wb") as f:
            f.write(response.content)
        return path
    return None


def log(action, text, noprint=False):
    with open("logfile.txt", "a+") as logfile:
        logfile.write(f"{action} {text}\n")
    if noprint:
        return

    if action == "[SEPARATOR]":
        print(action, text[0]*(columns-12))
    else:
        print(action, text)


def print_selection(dict_list):
    if not dict_list:
        print("No items to display.")
        return

    show_image = can_display_images()

    for idx, item in enumerate(dict_list):
        print(f"\n\033[1m[{idx}]\033[0m")  # Bold index
        for key, value in item.items():
            if key == "image_url" and value:
                if show_image:
                    show_image_in_kitty(value)
            elif value:  # Skip empty fields for clarity
                print(f"  \033[94m{key.capitalize():<10}\033[0m: {value}")
        print("-"*columns)
    print("\nSelect an item by index")


def progress_bar(full, fill):
    empty = full-fill

    factor = 50
    progress = "#"*int(fill/factor) + " "*int(empty/factor)

    percentage = 100*(fill/full)
    print(f"{percentage}%", progress)


def can_display_images():
    # TODO check if terminal can display images
    return True


def show_image_in_kitty(image_path):
    subprocess.run([
        "kitty",
        "+kitten",
        "icat",
        "--align",
        "left",
        image_path,
        ])
