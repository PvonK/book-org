def beautifulprint(dict_list):
    if not dict_list:
        print("No items to display.")
        return

    for idx, item in enumerate(dict_list):
        print(f"\n\033[1m[{idx}]\033[0m")  # Bold index
        for key, value in item.items():
            if value:  # Skip empty fields for clarity
                print(f"  \033[94m{key.capitalize():<10}\033[0m: {value}")
    print("\nSelect an item by index")


def progress_bar(full, fill):
    empty = full-fill

    factor = 50
    progress = "#"*int(fill/factor) + " "*int(empty/factor)

    percentage = 100*(fill/full)
    print(f"{percentage}%", progress)
