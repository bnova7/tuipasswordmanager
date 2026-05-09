import pytest
from unittest.mock import patch, MagicMock
import passwordmanager
import cli


def test_cli_add_entry():
    """Test adding an entry through the CLI menu."""
    vault = {"accounts": []}
    master_password = "test_password"
    salt = b"test_salt_16_bytes"

    # Mock the inputs: choice "1" (add), site, username, password, then "5" (exit)
    with patch('builtins.input', side_effect=["1", "example.com", "user@example", "5"]), \
         patch.object(cli, 'getpass', return_value="secret123"), \
         patch.object(cli, 'save_vault') as mock_save:

        cli.run_cli(vault, master_password, salt)

        # Check that the entry was added
        assert len(vault["accounts"]) == 1
        entry = vault["accounts"][0]
        assert entry["site"] == "example.com"
        assert entry["username"] == "user@example"
        assert entry["password"] == "secret123"

        # Check that save_vault was called on exit
        mock_save.assert_called_once_with(master_password, vault, salt)


def test_cli_view_entry():
    """Test viewing an entry through the CLI menu."""
    vault = {
        "accounts": [
            {"site": "github.com", "username": "testuser", "password": "mypass123"}
        ]
    }
    master_password = "test_password"
    salt = b"test_salt_16_bytes"

    # Mock inputs: choice "2" (view), index "0", "n" (no copy), "5" (exit)
    with patch('builtins.input', side_effect=["2", "0", "n", "5"]), \
         patch.object(cli, 'save_vault') as mock_save, \
         patch('builtins.print') as mock_print:

        cli.run_cli(vault, master_password, salt)

        # Check that the entry details were printed
        print_calls_str = ' '.join([str(call.args) for call in mock_print.call_args_list])
        assert "Saved entries" in print_calls_str
        assert "0: github.com" in print_calls_str
        assert "Entry" in print_calls_str
        assert "github.com" in print_calls_str
        assert "testuser" in print_calls_str
        assert "mypass123" in print_calls_str

        mock_save.assert_called_once()


def test_cli_delete_entry():
    """Test deleting an entry through the CLI menu."""
    vault = {
        "accounts": [
            {"site": "site1.com", "username": "user1", "password": "pass1"},
            {"site": "site2.com", "username": "user2", "password": "pass2"}
        ]
    }
    master_password = "test_password"
    salt = b"test_salt_16_bytes"

    # Mock inputs: choice "3" (delete), index "0", "5" (exit)
    with patch('builtins.input', side_effect=["3", "0", "5"]), \
         patch.object(cli, 'save_vault') as mock_save, \
         patch('builtins.print') as mock_print:

        cli.run_cli(vault, master_password, salt)

        # Check that the entry was deleted
        assert len(vault["accounts"]) == 1
        assert vault["accounts"][0]["site"] == "site2.com"

        # Check print output
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert "Removed entry for site1.com" in print_calls

        mock_save.assert_called_once()


def test_cli_invalid_choice():
    """Test handling of invalid menu choice."""
    vault = {"accounts": []}
    master_password = "test_password"
    salt = b"test_salt_16_bytes"

    # Mock inputs: invalid choice "99", then "5" (exit)
    with patch('builtins.input', side_effect=["99", "5"]), \
         patch.object(cli, 'save_vault') as mock_save, \
         patch('builtins.print') as mock_print:

        cli.run_cli(vault, master_password, salt)

        # Check that invalid choice message was printed
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert "Invalid option. Please choose a number from 1 to 5." in print_calls

        mock_save.assert_called_once()


def test_cli_keyboard_interrupt():
    """Test handling of KeyboardInterrupt (Ctrl+C)."""
    vault = {"accounts": []}
    master_password = "test_password"
    salt = b"test_salt_16_bytes"

    # Mock input to raise KeyboardInterrupt
    with patch('builtins.input', side_effect=KeyboardInterrupt), \
         patch.object(cli, 'save_vault') as mock_save, \
         patch('builtins.print') as mock_print:

        cli.run_cli(vault, master_password, salt)

        # Check that save was called and goodbye message printed
        mock_save.assert_called_once_with(master_password, vault, salt)
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert "\nVault saved. Goodbye." in print_calls