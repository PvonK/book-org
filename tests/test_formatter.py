import os
import pytest
from unittest.mock import patch
from book_org import formatter

LOGFILE = "logfile.txt"


@pytest.fixture(autouse=True)
def cleanup_logfile():
    # Cleanup before and after each test
    if os.path.exists(LOGFILE):
        os.remove(LOGFILE)
    yield
    if os.path.exists(LOGFILE):
        os.remove(LOGFILE)


def test_log_writes_to_file_and_prints(capfd):
    formatter.log("[INFO]", "Test message")
    assert os.path.exists(LOGFILE)

    with open(LOGFILE) as f:
        assert "[INFO] Test message" in f.read()

    out, _ = capfd.readouterr()
    assert "[INFO] Test message" in out


def test_log_no_print(capfd):
    formatter.log("[WARNING]", "Hidden message", noprint=True)
    out, _ = capfd.readouterr()
    assert "Hidden message" not in out


@patch("os.get_terminal_size", return_value=os.terminal_size((80, 24)))
def test_log_separator_prints_correct_line(mock_term, capfd):
    formatter.log("[SEPARATOR]", "=")
    out, _ = capfd.readouterr()
    assert "[SEPARATOR]" in out
    assert "=" * (80 - 12) in out


def test_print_selection_empty(capfd):
    formatter.print_selection([])
    out, _ = capfd.readouterr()
    assert "No items to display." in out


@patch("book_org.formatter.can_display_images", return_value=False)
def test_print_selection_output(mock_display_images, capfd):
    data = [
        {
            "title": "Test Book",
            "authors": "Jane Doe",
            "image_url": "http://example.com/image.jpg"
        }
    ]
    formatter.print_selection(data)
    out, _ = capfd.readouterr()
    assert "[0]" in out
    assert "Test Book" in out
    assert "Jane Doe" in out
    assert "image_url" not in out  # Not shown if image display is disabled


def test_progress_bar_output(capfd):
    formatter.columns = 50
    formatter.progress_bar(10, 5)
    out, _ = capfd.readouterr()
    assert "50.0%" in out
    assert "#" in out


def test_can_display_images_returns_true():
    assert formatter.can_display_images() is True


@patch("subprocess.run")
def test_show_image_in_kitty_runs_subprocess(mock_run):
    formatter.show_image_in_kitty("some_image.png")
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert "kitty" in args and "icat" in args


def test_log_with_unicode_and_special_chars(capfd):
    message = "Testing ✨🚀🔥 special chars & unicode"
    formatter.log("[DEBUG]", message)
    with open(LOGFILE) as f:
        assert message in f.read()

    out, _ = capfd.readouterr()
    assert message in out


@patch("book_org.formatter.can_display_images", return_value=False)
def test_print_selection_missing_fields(mock_img, capfd):
    data = [
        {
            "title": "Only Title",
            "authors": "",  # should be skipped
            "publisher": None,  # should be skipped
        }
    ]
    formatter.print_selection(data)
    out, _ = capfd.readouterr()
    assert "Only Title" in out
    assert "authors" not in out.lower()
    assert "publisher" not in out.lower()


@patch("os.get_terminal_size", return_value=os.terminal_size((200, 24)))
def test_log_separator_with_large_terminal(mock_term, capfd):
    formatter.columns = 200
    formatter.log("[SEPARATOR]", "-")
    out, _ = capfd.readouterr()
    assert "-" * (200 - 12) in out


@patch("book_org.formatter.get_terminal_columns", return_value=0)
def test_progress_bar_tiny_terminal(mock_get_cols, capfd):
    # Should skip printing entirely when terminal is too small
    formatter.progress_bar(10, 5)
    out, _ = capfd.readouterr()
    assert out.strip() == ""  # Nothing printed due to small terminal


@patch("book_org.formatter.get_terminal_columns", return_value=50)
def test_progress_bar_zero_total(mock_get_cols, capfd):
    formatter.progress_bar(0, 5)
    out, _ = capfd.readouterr()
    assert "100%" in out
    assert "#"*44 in out


@patch("subprocess.run", side_effect=Exception("Kitty failed"))
def test_show_image_in_kitty_fails_gracefully(mock_run):
    try:
        formatter.show_image_in_kitty("fake.png")  # Should not raise
    except Exception:
        pytest.fail("Exception should be caught internally")
