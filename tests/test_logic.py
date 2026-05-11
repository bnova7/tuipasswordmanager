import json
import os
import pytest
from unittest.mock import patch, MagicMock
from cryptography.exceptions import InvalidTag

from vault import CryptoService, Vault, VaultService
from passwordmanager import check_password_strength, edit_entry
import passwordgenerator


@patch('passwordgenerator.secrets.choice')
def test_password_generator(mock_choice):
    mock_choice.side_effect = ['a', 'B', 'c', 'D', 'e', 'F', 'g', 'H', 'i', 'J', 'k', 'L', 'm', 'N', 'o', 'P']
    password = passwordgenerator.generate_password(16)
    assert len(password) == 16
    assert password == 'aBcDeFgHiJkLmNoP'


def test_password_generator_custom_length():
    password = passwordgenerator.generate_password(32)
    assert len(password) == 32


def test_copy_to_clipboard_success():
    with patch('passwordgenerator.pyperclip.copy') as mock_copy:
        passwordgenerator.copy_to_clipboard("mypassword")
        mock_copy.assert_called_once_with("mypassword")


def test_copy_to_clipboard_unavailable():
    with patch('passwordgenerator.pyperclip.copy', side_effect=passwordgenerator.pyperclip.PyperclipException), \
         patch('builtins.print') as mock_print:
        passwordgenerator.copy_to_clipboard("mypassword")
        mock_print.assert_called_once_with("Warning: clipboard is not available on this platform.")


def test_generator_main_chooses_to_copy():
    with patch('builtins.input', return_value="y"), \
         patch('passwordgenerator.generate_password', return_value="FakePass1!XXXXXX"), \
         patch('passwordgenerator.pyperclip.copy') as mock_copy, \
         patch('builtins.print'):
        passwordgenerator.main()
        mock_copy.assert_called_once_with("FakePass1!XXXXXX")


def test_generator_main_chooses_not_to_copy():
    with patch('builtins.input', return_value="n"), \
         patch('passwordgenerator.pyperclip.copy') as mock_copy, \
         patch('builtins.print'):
        passwordgenerator.main()
        mock_copy.assert_not_called()


def test_generator_main_keyboard_interrupt():
    with patch('builtins.input', side_effect=KeyboardInterrupt), \
         patch('builtins.print') as mock_print:
        passwordgenerator.main()
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert "\nGoodbye." in print_calls


def test_derive_key():
    password = "test_password"
    salt = os.urandom(16)

    key1 = CryptoService.derive_key(password, salt)
    key2 = CryptoService.derive_key(password, salt)

    assert key1 == key2
    assert len(key1) == 32


def test_vault_creation_and_opening(tmp_path):
    vault_file = tmp_path / "vault.json"
    test_password = "test_master_password"

    service = VaultService(CryptoService(), str(vault_file))
    vault, salt = service.create_vault(test_password)

    assert vault is not None
    assert salt is not None
    assert vault.accounts == []

    opened_vault, opened_salt = service.load_vault(test_password)
    assert opened_vault.accounts == vault.accounts
    assert opened_salt == salt


def test_vault_open_wrong_password(tmp_path):
    vault_file = tmp_path / "vault.json"
    service = VaultService(CryptoService(), str(vault_file))
    service.create_vault("correct_password")

    with pytest.raises(InvalidTag):
        service.load_vault("wrong_password")


def test_vault_load_missing_file(tmp_path):
    vault_file = tmp_path / "nonexistent.json"
    service = VaultService(CryptoService(), str(vault_file))

    with pytest.raises(FileNotFoundError):
        service.load_vault("any_password")


def test_vault_load_corrupt_json(tmp_path):
    vault_file = tmp_path / "vault.json"
    vault_file.write_text("this is not valid json")
    service = VaultService(CryptoService(), str(vault_file))

    with pytest.raises(json.JSONDecodeError):
        service.load_vault("any_password")


def test_vault_load_missing_fields(tmp_path):
    vault_file = tmp_path / "vault.json"
    vault_file.write_text('{"foo": "bar"}')
    service = VaultService(CryptoService(), str(vault_file))

    with pytest.raises(KeyError):
        service.load_vault("any_password")


def test_vault_load_invalid_hex(tmp_path):
    vault_file = tmp_path / "vault.json"
    vault_file.write_text('{"salt": "ZZZZ", "nonce": "ZZZZ", "ciphertext": "ZZZZ"}')
    service = VaultService(CryptoService(), str(vault_file))

    with pytest.raises(ValueError):
        service.load_vault("any_password")


def test_add_entry():
    vault = Vault()
    entry = vault.add_entry("example.com", "user@example.com", "secret123")

    assert len(vault.accounts) == 1
    assert entry["site"] == "example.com"
    assert vault.accounts[0]["site"] == "example.com"


def test_delete_entry():
    vault = Vault([
        {"site": "site1.com", "username": "user1", "password": "pass1"},
        {"site": "site2.com", "username": "user2", "password": "pass2"},
    ])

    removed = vault.delete_entry(0)
    assert removed["site"] == "site1.com"
    assert len(vault.accounts) == 1
    assert vault.accounts[0]["site"] == "site2.com"


def test_vault_round_trip(tmp_path):
    vault_file = tmp_path / "vault.json"
    test_password = "secure_password"

    service = VaultService(CryptoService(), str(vault_file))
    vault, salt = service.create_vault(test_password)
    vault.add_entry("github.com", "myuser", "mypass123")

    service.save_vault(test_password, vault, salt)
    opened_vault, _ = service.load_vault(test_password)

    assert len(opened_vault.accounts) == 1
    assert opened_vault.accounts[0]["site"] == "github.com"
    assert opened_vault.accounts[0]["username"] == "myuser"


# --- check_password_strength ---

def test_password_strength_valid():
    assert check_password_strength("ValidPass1!ValidP") is True


def test_password_strength_exactly_16_chars():
    assert check_password_strength("ValidPass1!VPass") is True


def test_password_strength_too_short():
    # 15 chars, otherwise meets all criteria
    assert check_password_strength("ValidPass1!Val") is False


def test_password_strength_empty():
    assert check_password_strength("") is False


def test_password_strength_no_uppercase():
    assert check_password_strength("validpass1!validp") is False


def test_password_strength_no_lowercase():
    assert check_password_strength("VALIDPASS1!VALIDP") is False


def test_password_strength_no_digit():
    assert check_password_strength("ValidPass!!ValidP") is False


def test_password_strength_no_special_char():
    assert check_password_strength("ValidPass1ValidPa") is False


def test_password_strength_unrecognised_special_char():
    # ~ and ' are not in the allowed special character set
    assert check_password_strength("ValidPass1~ValidP") is False
    assert check_password_strength("ValidPass1'ValidP") is False


def test_password_strength_each_allowed_special_char():
    # Every character in the allowed set should satisfy the special-char requirement
    allowed = "!@#$%^&*()-_=+[]{}|;:,.<>?/"
    for ch in allowed:
        password = f"ValidPass1{ch}VVVVV"
        assert check_password_strength(password) is True, f"Failed for special char: {ch!r}"


# --- edit_entry ---

def test_edit_entry_updates_all_fields():
    vault = Vault([{"site": "old.com", "username": "olduser", "password": "OldPass1!OldPass"}])
    vault_service = MagicMock()

    with patch('builtins.input', side_effect=["new.com", "newuser"]), \
         patch('passwordmanager.get_password', return_value="NewPass1!NewPass"), \
         patch('builtins.print'):
        edit_entry(vault, 0, "master", b"salt", vault_service)

    assert vault.accounts[0]["site"] == "new.com"
    assert vault.accounts[0]["username"] == "newuser"
    assert vault.accounts[0]["password"] == "NewPass1!NewPass"
    vault_service.save_vault.assert_called_once_with("master", vault, b"salt")


def test_edit_entry_keeps_current_values_when_blank():
    vault = Vault([{"site": "old.com", "username": "olduser", "password": "OldPass1!OldPass"}])
    vault_service = MagicMock()

    with patch('builtins.input', side_effect=["", ""]), \
         patch('passwordmanager.get_password', return_value=""), \
         patch('builtins.print'):
        edit_entry(vault, 0, "master", b"salt", vault_service)

    assert vault.accounts[0]["site"] == "old.com"
    assert vault.accounts[0]["username"] == "olduser"
    assert vault.accounts[0]["password"] == "OldPass1!OldPass"
    vault_service.save_vault.assert_called_once()


def test_edit_entry_invalid_index():
    vault = Vault([{"site": "old.com", "username": "olduser", "password": "OldPass1!OldPass"}])
    vault_service = MagicMock()

    with patch('builtins.print') as mock_print:
        edit_entry(vault, 99, "master", b"salt", vault_service)

    print_calls = [call.args[0] for call in mock_print.call_args_list]
    assert "Invalid index." in print_calls
    vault_service.save_vault.assert_not_called()


def test_edit_entry_keyboard_interrupt():
    vault = Vault([{"site": "old.com", "username": "olduser", "password": "OldPass1!OldPass"}])
    vault_service = MagicMock()

    with patch('builtins.input', side_effect=KeyboardInterrupt), \
         patch('builtins.print') as mock_print:
        edit_entry(vault, 0, "master", b"salt", vault_service)

    print_calls = [call.args[0] for call in mock_print.call_args_list]
    assert "\nGoodbye." in print_calls
    vault_service.save_vault.assert_not_called()
