# tests/test_core.py

from unittest.mock import patch, MagicMock
from book_org import core


def test_is_ext_valid_accepts_valid_extensions():
    for ext in core.valid_file_extensions:
        assert core.is_ext_valid(ext) is True


def test_is_ext_valid_rejects_invalid_extension():
    assert not core.is_ext_valid(".invalid")


def test_find_all_files_filters_extensions(tmp_path):
    # Create valid files for all extensions defined in config
    valid_files = []
    for ext in core.valid_file_extensions:
        file_path = tmp_path / f"valid{ext}"
        file_path.write_text("dummy")
        valid_files.append(str(file_path))

    # Create an invalid extension file
    invalid_file = tmp_path / "invalid.mp3"
    invalid_file.write_text("dummy")

    files = core.find_all_files(str(tmp_path))

    # Assert all valid files are found
    for valid_file in valid_files:
        assert valid_file in files

    # Assert invalid file is excluded
    assert str(invalid_file) not in files


@patch("book_org.core.Book")
@patch("book_org.core.move_book")
@patch("book_org.core.progress_bar")
@patch("book_org.core.find_all_files")
@patch("os.path.isfile")
def test_organize_dir_directory_mode(
    mock_isfile,
    mock_find_all,
    mock_progress,
    mock_move,
    mock_book_class,
):
    # Return False for directory ("test_dir"), True for files
    mock_isfile.side_effect = lambda path: path != "test_dir"
    mock_find_all.return_value = ["book1.epub", "book2.epub"]

    mock_book = MagicMock()
    mock_book_class.return_value = mock_book

    core.organize_dir(
        "test_dir",
        dry=True,
        interactive=True,
        output_path_dir="organized"
    )

    # Book should be instantiated once per file found
    assert mock_book_class.call_count == 2
    # organize_book should be called on the mock Book instance for each file
    assert mock_book.organize_book.call_count == 2
    # move_book should be called for each file (with dry=True)
    assert mock_move.call_count == 2
    # progress_bar should be called twice: after each file
    assert mock_progress.call_count == 2


@patch("book_org.core.Book")
@patch("os.path.isfile")
def test_organize_dir_single_file_mode(mock_isfile, mock_book_class):
    # simulate input is a single file
    mock_isfile.return_value = True
    mock_book = MagicMock()
    mock_book_class.return_value = mock_book

    core.organize_dir("book.epub", interactive=False, output_path_dir=None)

    mock_book_class.assert_called_once_with(
        "book.epub",
        interactive_organizer=False,
        output_path_dir=None,
    )
    mock_book.organize_book.assert_called_once()


def test_standardize_categories_stub():
    class DummyBook:
        def __init__(self, categories):
            self.metadata = type("Meta", (), {"categories": categories})()

    books = [DummyBook(["sci-fi"]), DummyBook(["SciFi"])]
    # Currently does nothing, but it should not crash
    core.standardize_categories(books)
