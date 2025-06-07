
import os
from unittest.mock import patch
from book_org.file_sorter import link_file, move_book


class DummyBook:
    def __init__(self):
        self.fullpath = "/path/to/original/book.pdf"
        self.new_fullpath = "/organized_books/Category/book - title (2025) \
            [12345].pdf"
        self.new_path = "/organized_books/Category"
        self.categories = ["Category", "AnotherCategory"]
        self.output_path_dir = "/organized_books"
        self.filename = "book.pdf"
        self.new_filename = "book - title (2025) [12345].pdf"


@patch("book_org.file_sorter.os.symlink")
def test_link_file_symlink_called(mock_symlink):
    src = "/src/file"
    dst = "/dst/file"
    link_file(src, dst)
    mock_symlink.assert_called_once_with(src, dst)


@patch("book_org.file_sorter.os.symlink")
def test_link_file_ignores_fileexistserror(mock_symlink):
    mock_symlink.side_effect = FileExistsError
    # Should not raise despite the exception
    link_file("/src", "/dst")


@patch("book_org.file_sorter.os.rename")
@patch("book_org.file_sorter.os.makedirs")
@patch("book_org.file_sorter.log")
@patch("book_org.file_sorter.link_file")
# also tests links when more than one category
def test_move_book_moves_and_creates_dirs(
        mock_link_file,
        mock_log,
        mock_makedirs,
        mock_rename
        ):
    dummy_book = DummyBook()

    move_book(dummy_book, dry=False)

    # Verify directory creation for main path
    mock_makedirs.assert_any_call(dummy_book.new_path, exist_ok=True)
    # Verify file move called with os.rename
    mock_rename.assert_called_once_with(
        dummy_book.fullpath,
        dummy_book.new_fullpath
        )
    # Verify log for move
    mock_log.assert_any_call(
        "[move]", f"'{dummy_book.fullpath}' => '{dummy_book.new_fullpath}'"
        )

    # Verify symlink creation for additional categories
    for cat in dummy_book.categories[1:]:
        expected_dir = os.path.join(dummy_book.output_path_dir, cat)
        expected_link = os.path.join(expected_dir, dummy_book.new_filename)
        mock_makedirs.assert_any_call(expected_dir, exist_ok=True)
        mock_log.assert_any_call(
            "[link]", f"'{dummy_book.new_fullpath}' => '{expected_link}'"
            )
        mock_link_file.assert_any_call(dummy_book.new_fullpath, expected_link)


@patch("book_org.file_sorter.link_file")
@patch("book_org.file_sorter.os.makedirs")
@patch("book_org.file_sorter.log")
def test_move_book_dry_runs_use_link_file_one_category(
        mock_log,
        mock_makedirs,
        mock_link_file
        ):
    dummy_book = DummyBook()
    dummy_book.categories = ["Category"]

    move_book(dummy_book, dry=True)

    # Directory creation called
    mock_makedirs.assert_any_call(dummy_book.new_path, exist_ok=True)
    # Uses link_file instead of os.rename
    mock_link_file.assert_called_once_with(
        dummy_book.fullpath, dummy_book.new_fullpath
        )
    # Logs move operation
    mock_log.assert_any_call(
        "[move]", f"'{dummy_book.fullpath}' => '{dummy_book.new_fullpath}'"
        )


@patch("book_org.file_sorter.os.rename")
@patch("book_org.file_sorter.os.makedirs")
@patch("book_org.file_sorter.log")
def test_move_book_no_new_fullpath_moves_to_no_metadata(
        mock_log,
        mock_makedirs,
        mock_rename
        ):
    dummy = DummyBook()
    dummy.new_fullpath = None
    dummy.categories = []
    dummy.output_path_dir = "/organized_books"
    dummy.filename = "book.pdf"
    dummy.fullpath = "/path/to/book.pdf"

    move_book(dummy, dry=False)

    expected_dir = os.path.join(dummy.output_path_dir, "no-metadata")
    expected_path = os.path.join(expected_dir, dummy.filename)

    # Check directory created for no-metadata
    mock_makedirs.assert_called_once_with(expected_dir, exist_ok=True)
    # Check rename called to move file to no-metadata folder
    mock_rename.assert_called_once_with(dummy.fullpath, expected_path)
    # Check log for move
    mock_log.assert_called_once_with(
        "[move]", f"'{dummy.fullpath}' => '{expected_path}'"
        )
