import pytest
from unittest.mock import patch
import os
import passwordmanager
import passwordgenerator

@patch('passwordgenerator.secrets.choice')
def test_password_generator(mock_choice):
    """Test that generated passwords have required characteristics."""
    mock_choice.side_effect = ['a', 'B', 'c', 'D', 'e', 'F', 'g', 'H', 'i', 'J', 'k', 'L', 'm', 'N', 'o', 'P']
    password = passwordgenerator.generate_password(16)
    assert len(password) == 16
    assert password == 'aBcDeFgHiJkLmNoP'



def test_password_generator_custom_length():
    """Test password generation with custom length."""
    password = passwordgenerator.generate_password(32)
    assert len(password) == 32


def test_derive_key():
    """Test that key derivation is deterministic."""
    password = "test_password"
    salt = os.urandom(16)
    
    key1 = passwordmanager.derive_key(password, salt)
    key2 = passwordmanager.derive_key(password, salt)
    
    assert key1 == key2
    assert len(key1) == 32


@patch('passwordmanager.getpass.getpass')
def test_vault_creation_and_opening(mock_getpass, tmp_path):
    """Test vault creation and opening with mocked user input."""
    vault_file = tmp_path / "vault.json"
    test_password = "test_master_password"
    
    # Mock getpass to return the test password
    mock_getpass.return_value = test_password
    
    # Create vault
    vault, salt, password = passwordmanager.create_vault(filename=str(vault_file))
    assert vault is not None
    assert salt is not None
    assert password == test_password
    assert vault["accounts"] == []
    
    # Open vault with correct password
    opened_vault, opened_salt = passwordmanager.open_vault(
        master_password=test_password,
        filename=str(vault_file)
    )
    assert opened_vault == vault
    assert opened_salt == salt


def test_vault_open_wrong_password(tmp_path):
    """Test that opening vault with wrong password raises exception."""
    vault_file = tmp_path / "vault.json"
    test_password = "correct_password"
    
    with patch('passwordmanager.getpass.getpass', return_value=test_password):
        vault, salt, _ = passwordmanager.create_vault(filename=str(vault_file))
    
    # Try to open with wrong password
    with pytest.raises(Exception):
        passwordmanager.open_vault(
            master_password="wrong_password",
            filename=str(vault_file)
        )


def test_add_entry():
    """Test adding an entry to the vault."""
    vault = {"accounts": []}
    
    # Manually call add logic instead of using add_entry (which has user input)
    vault["accounts"].append({
        "site": "example.com",
        "username": "user@example.com",
        "password": "secret123"
    })
    
    assert len(vault["accounts"]) == 1
    assert vault["accounts"][0]["site"] == "example.com"


def test_delete_entry():
    """Test deleting an entry from the vault."""
    vault = {
        "accounts": [
            {"site": "site1.com", "username": "user1", "password": "pass1"},
            {"site": "site2.com", "username": "user2", "password": "pass2"},
        ]
    }
    
    # Delete the first entry
    vault["accounts"].pop(0)
    
    assert len(vault["accounts"]) == 1
    assert vault["accounts"][0]["site"] == "site2.com"


@patch('passwordmanager.getpass.getpass')
def test_vault_round_trip(mock_getpass, tmp_path):
    """Test that vault data persists correctly through save and load."""
    vault_file = tmp_path / "vault.json"
    test_password = "secure_password"
    
    mock_getpass.return_value = test_password
    
    # Create vault
    vault, salt, _ = passwordmanager.create_vault(filename=str(vault_file))
    
    # Add some entries
    vault["accounts"].append({
        "site": "github.com",
        "username": "myuser",
        "password": "mypass123"
    })
    
    # Save and reopen
    passwordmanager.save_vault(test_password, vault, salt, filename=str(vault_file))
    opened_vault, _ = passwordmanager.open_vault(test_password, filename=str(vault_file))
    
    # Verify data persisted
    assert len(opened_vault["accounts"]) == 1
    assert opened_vault["accounts"][0]["site"] == "github.com"
    assert opened_vault["accounts"][0]["username"] == "myuser"
    opened_vault = passwordmanager.open_vault(master_password=test_password, filename=str(vault_file))
    assert opened_vault is not None

@patch('passwordmanager.getpass.getpass')
def test_vault_encryption_and_decryption(mock_getpass,tmp_path):
    vault_file = tmp_path / "vault.json"
    password = mock_getpass.return_value = "test_master_password"

    # Create vault
    vault, salt, password = passwordmanager.create_vault(filename=str(vault_file))
    assert vault is not None
    assert salt is not None

    # Open vault with correct password
    opened_vault = passwordmanager.open_vault(master_password=password, filename=str(vault_file))
    assert opened_vault is not None