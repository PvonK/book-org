# tests/test_cli.py

import sys
from unittest.mock import patch
from book_org.cli import parse_args, main


@patch("book_org.cli.organize_dir")
def test_main_calls_organize_dir(mock_organize):
    test_args = ["prog", "books", "-o", "organized", "-d", "-r", "-i"]
    with patch.object(sys, "argv", test_args):
        main()

    mock_organize.assert_called_once_with(
        "books",
        dry=True,
        interactive=True,
        output_path_dir="organized"
    )


def test_parse_args_basic(monkeypatch):
    test_args = ["prog", "myfolder"]
    monkeypatch.setattr(sys, "argv", test_args)

    args = parse_args()
    assert args.directory == "myfolder"
    assert args.output is None
    assert not args.dryrun
    assert not args.recursive
    assert not args.interactive


def test_parse_args_all_flags(monkeypatch):
    test_args = ["prog", "source", "-o", "dest", "-d", "-r", "-i"]
    monkeypatch.setattr(sys, "argv", test_args)

    args = parse_args()
    assert args.directory == "source"
    assert args.output == "dest"
    assert args.dryrun
    assert args.recursive
    assert args.interactive
