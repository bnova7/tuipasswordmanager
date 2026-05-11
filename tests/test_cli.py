from unittest.mock import patch, MagicMock
from vault import Vault
import cli


def _mock_vault_service():
    return MagicMock()


def test_cli_add_entry():
    vault = Vault()
    master_password = "test_password"
    salt = b"test_salt_16_bytes"
    vault_service = _mock_vault_service()

    with patch('builtins.input', side_effect=["1", "example.com", "user@example", "5"]), \
         patch.object(cli, 'getpass', return_value="secret123"):

        cli.run_cli(vault, master_password, salt, vault_service)

        assert len(vault.accounts) == 1
        entry = vault.accounts[0]
        assert entry["site"] == "example.com"
        assert entry["username"] == "user@example"
        assert entry["password"] == "secret123"

        assert vault_service.save_vault.call_count == 2
        vault_service.save_vault.assert_called_with(master_password, vault, salt)


def test_cli_view_entry():
    vault = Vault([
        {"site": "github.com", "username": "testuser", "password": "mypass123"}
    ])
    master_password = "test_password"
    salt = b"test_salt_16_bytes"
    vault_service = _mock_vault_service()

    with patch('builtins.input', side_effect=["2", "0", "n", "5"]), \
         patch('builtins.print') as mock_print:

        cli.run_cli(vault, master_password, salt, vault_service)

        print_calls_str = ' '.join([str(call.args) for call in mock_print.call_args_list])
        assert "Saved entries" in print_calls_str
        assert "0: github.com" in print_calls_str
        assert "Entry" in print_calls_str
        assert "github.com" in print_calls_str
        assert "testuser" in print_calls_str
        assert "mypass123" in print_calls_str

        vault_service.save_vault.assert_called_once()


def test_cli_delete_entry():
    vault = Vault([
        {"site": "site1.com", "username": "user1", "password": "pass1"},
        {"site": "site2.com", "username": "user2", "password": "pass2"}
    ])
    master_password = "test_password"
    salt = b"test_salt_16_bytes"
    vault_service = _mock_vault_service()

    with patch('builtins.input', side_effect=["3", "0", "5"]), \
         patch('builtins.print') as mock_print:

        cli.run_cli(vault, master_password, salt, vault_service)

        assert len(vault.accounts) == 1
        assert vault.accounts[0]["site"] == "site2.com"

        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert "Removed entry for site1.com" in print_calls

        assert vault_service.save_vault.call_count == 2
        vault_service.save_vault.assert_called_with(master_password, vault, salt)


def test_cli_invalid_choice():
    vault = Vault()
    master_password = "test_password"
    salt = b"test_salt_16_bytes"
    vault_service = _mock_vault_service()

    with patch('builtins.input', side_effect=["99", "5"]), \
         patch('builtins.print') as mock_print:

        cli.run_cli(vault, master_password, salt, vault_service)

        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert "Invalid option. Please choose a number from 1 to 5." in print_calls

        vault_service.save_vault.assert_called_once()


def test_cli_keyboard_interrupt():
    vault = Vault()
    master_password = "test_password"
    salt = b"test_salt_16_bytes"
    vault_service = _mock_vault_service()

    with patch('builtins.input', side_effect=KeyboardInterrupt), \
         patch('builtins.print') as mock_print:

        cli.run_cli(vault, master_password, salt, vault_service)

        vault_service.save_vault.assert_called_once_with(master_password, vault, salt)
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert "\nVault saved. Goodbye." in print_calls


def test_cli_view_entry_copies_to_clipboard():
    vault = Vault([
        {"site": "github.com", "username": "testuser", "password": "mypass123"}
    ])
    master_password = "test_password"
    salt = b"test_salt_16_bytes"
    vault_service = _mock_vault_service()

    with patch('builtins.input', side_effect=["2", "0", "y", "5"]), \
         patch('cli.pyperclip.copy') as mock_copy, \
         patch('builtins.print'):
        cli.run_cli(vault, master_password, salt, vault_service)
        mock_copy.assert_called_once_with("mypass123")


def test_cli_edit_entry():
    vault = Vault([{"site": "old.com", "username": "olduser", "password": "OldPass1!OldPass"}])
    master_password = "test_password"
    salt = b"test_salt_16_bytes"
    vault_service = _mock_vault_service()

    with patch('builtins.input', side_effect=["7", "0", "new.com", "newuser", "5"]), \
         patch('passwordmanager.get_password', return_value="NewPass1!NewPass"), \
         patch('builtins.print'):
        cli.run_cli(vault, master_password, salt, vault_service)

    assert vault.accounts[0]["site"] == "new.com"
    assert vault.accounts[0]["username"] == "newuser"
    assert vault.accounts[0]["password"] == "NewPass1!NewPass"
    assert vault_service.save_vault.call_count == 2


def test_cli_view_entry_clipboard_unavailable():
    vault = Vault([
        {"site": "github.com", "username": "testuser", "password": "mypass123"}
    ])
    master_password = "test_password"
    salt = b"test_salt_16_bytes"
    vault_service = _mock_vault_service()

    with patch('builtins.input', side_effect=["2", "0", "y", "5"]), \
         patch('cli.pyperclip.copy', side_effect=cli.pyperclip.PyperclipException), \
         patch('builtins.print') as mock_print:
        cli.run_cli(vault, master_password, salt, vault_service)
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert "Clipboard is unavailable on this platform." in print_calls
