import os
import pytest
from unittest.mock import patch

import passwordmanager
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


def test_derive_key():
    password = "test_password"
    salt = os.urandom(16)

    key1 = passwordmanager.derive_key(password, salt)
    key2 = passwordmanager.derive_key(password, salt)

    assert key1 == key2
    assert len(key1) == 32


def test_vault_creation_and_opening(tmp_path):
    vault_file = tmp_path / "vault.json"
    test_password = "test_master_password"

    vault, salt, password = passwordmanager.create_vault(test_password, filename=str(vault_file))
    assert vault is not None
    assert salt is not None
    assert password == test_password
    assert vault["accounts"] == []

    opened_vault, opened_salt = passwordmanager.open_vault(
        master_password=test_password,
        filename=str(vault_file)
    )
    assert opened_vault == vault
    assert opened_salt == salt


def test_vault_open_wrong_password(tmp_path):
    vault_file = tmp_path / "vault.json"
    test_password = "correct_password"

    vault, salt, _ = passwordmanager.create_vault(test_password, filename=str(vault_file))

    with pytest.raises(Exception):
        passwordmanager.open_vault(
            master_password="wrong_password",
            filename=str(vault_file)
        )


def test_add_entry():
    vault = {"accounts": []}
    entry = passwordmanager.add_entry(vault, "example.com", "user@example.com", "secret123")

    assert len(vault["accounts"]) == 1
    assert entry["site"] == "example.com"
    assert vault["accounts"][0]["site"] == "example.com"


def test_delete_entry():
    vault = {
        "accounts": [
            {"site": "site1.com", "username": "user1", "password": "pass1"},
            {"site": "site2.com", "username": "user2", "password": "pass2"},
        ]
    }

    removed = passwordmanager.delete_entry(vault, 0)
    assert removed["site"] == "site1.com"
    assert len(vault["accounts"]) == 1
    assert vault["accounts"][0]["site"] == "site2.com"


def test_vault_round_trip(tmp_path):
    vault_file = tmp_path / "vault.json"
    test_password = "secure_password"

    vault, salt, _ = passwordmanager.create_vault(test_password, filename=str(vault_file))
    passwordmanager.add_entry(vault, "github.com", "myuser", "mypass123")

    passwordmanager.save_vault(test_password, vault, salt, filename=str(vault_file))
    opened_vault, _ = passwordmanager.open_vault(test_password, filename=str(vault_file))

    assert len(opened_vault["accounts"]) == 1
    assert opened_vault["accounts"][0]["site"] == "github.com"
    assert opened_vault["accounts"][0]["username"] == "myuser"
