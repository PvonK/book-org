# Book-org A python based ebook organizing script

This is a python script for organizing a vast ebook library with automated and/or interactive metadata fetching, file renaming and ebook categorizing.

##### Instructions:

1- install dependencies
2- run the script: `python organizer.py [directory-to-organize]`

### Script arguments:

##### Non optional:

[file/directory]      file or directory to organize: if a file is selected it will be ran through the parser and metadata finder and print the metadata found. If it is a directory, however, all books will be ran through the organizer and moved to a new directory under `./organized-books/[found-category]/`.

##### Optional:

-i    --interactive    Interactive mode: if there is little confidence that the book's fetched metadata is correct the user will be prompted to decide if it is or not.

-d    --dryrun         Dry run: do not modify the original book directory. At the moment it is not a "true dry run" mode since it does create directories and symlinks. It does so to make the testing during development easier than by parsing the logfile. On release, however, the script should not modify or create any files or directories if this setting is active.

