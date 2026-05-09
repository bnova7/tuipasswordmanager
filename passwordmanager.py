import argparse
import getpass
import json
import os
import pyperclip
import passwordgenerator
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


VAULT_FILE = "vault.json"
SALT_SIZE = 16
NONCE_SIZE = 12
KDF_ITERATIONS = 200_000


def check_password_strength(password: str) -> bool:
    """Basic password strength check."""
    if len(password) < 8:
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    if not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for c in password):
        return False
    return True

def get_master_password_confirm() -> str:
    try:
        password = getpass.getpass("Create master password: ")

        is_strong = check_password_strength(password)
        if not is_strong:
            print("Password is too weak. It must be at least 8 characters long and include uppercase, lowercase, digits, and special characters.")
            return get_master_password_confirm()
        
        confirm_password = getpass.getpass("Confirm master password: ")

        if password != confirm_password:
            print("Passwords do not match. Please try again.")
            return get_master_password_confirm()

        if not password:
            print("Password cannot be empty. Please try again.")
            return get_master_password_confirm()
    

        return password
    except KeyboardInterrupt:
        print("\nGoodbye.")
        exit(0)


def get_master_password() -> str:
    try:
        password = getpass.getpass("Enter master password: ")
        if not password:
            print("Password cannot be empty. Please try again.")
            return get_master_password()
        return password
    except KeyboardInterrupt:
        print("\nGoodbye.")
        exit(0)


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=KDF_ITERATIONS,
    )
    return kdf.derive(password.encode())


def save_vault(master_password: str, vault: dict, salt: bytes, filename: str = VAULT_FILE) -> None:
    key = derive_key(master_password, salt)
    aesgcm = AESGCM(key)
    nonce = os.urandom(NONCE_SIZE)
    plaintext = json.dumps(vault, separators=(",", ":")).encode()
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    data = {
        "salt": salt.hex(),
        "nonce": nonce.hex(),
        "ciphertext": ciphertext.hex(),
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f)


def open_vault(master_password: str, filename: str = VAULT_FILE) -> tuple[dict, bytes]:
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    salt = bytes.fromhex(data["salt"])
    nonce = bytes.fromhex(data["nonce"])
    ciphertext = bytes.fromhex(data["ciphertext"])
    key = derive_key(master_password, salt)
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)

    return json.loads(plaintext.decode()), salt


def create_vault(master_password: str, filename: str = VAULT_FILE) -> tuple[dict, bytes, str]:
    vault = {"accounts": []}
    salt = os.urandom(SALT_SIZE)
    save_vault(master_password, vault, salt, filename)
    return vault, salt, master_password


def add_entry(vault: dict, site: str, username: str, password: str) -> dict:
    if not site or not username or not password:
        raise ValueError("Site, username, and password are required.")

    entry = {
        "site": site,
        "username": username,
        "password": password,
    }
    vault["accounts"].append(entry)
    return entry


def list_entries(vault: dict) -> None:
    accounts = vault.get("accounts", [])
    if not accounts:
        print("No entries found.")
        return

    print("\nSaved entries:")
    for index, account in enumerate(accounts):
        print(f"{index}: {account['site']}")


def get_entry(vault: dict, index: int) -> dict | None:
    accounts = vault.get("accounts", [])
    if index < 0 or index >= len(accounts):
        return None
    return accounts[index]


def delete_entry(vault: dict, index: int) -> dict:
    accounts = vault.get("accounts", [])
    if index < 0 or index >= len(accounts):
        raise IndexError("Invalid index.")
    removed = accounts.pop(index)
    return removed


def run_manager() -> None:
    if not os.path.exists(VAULT_FILE):
        print("No vault found. Creating a new vault.")
        master_password = get_master_password_confirm()
        vault, salt, _ = create_vault(master_password, VAULT_FILE)
        print("Vault created successfully.")
    else:
        master_password = get_master_password()

        try:
            vault, salt = open_vault(master_password, VAULT_FILE)
            print("Vault unlocked.")
        except Exception:
            print("Failed to unlock vault. Please verify your password and try again.")
            return

    import cli
    cli.run_cli(vault, master_password, salt)



def main() -> None:
    parser = argparse.ArgumentParser(
        description="Terminal password manager with local encrypted vault."
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Create a secure password without opening the vault."
    )
    args = parser.parse_args()

    if args.generate:
        passwordgenerator.main()
        return

    run_manager()


if __name__ == "__main__":
    main()

    



