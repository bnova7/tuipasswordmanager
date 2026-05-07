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


def create_vault(filename: str = VAULT_FILE) -> tuple[dict, bytes, str]:
    print("No vault found. Creating a new vault.")

    while True:
        password = getpass.getpass("Create master password: ")
        confirm = getpass.getpass("Confirm master password: ")

        if not password:
            print("Master password cannot be empty. Please try again.")
            continue

        if password != confirm:
            print("Passwords do not match. Please try again.")
            continue

        break

    vault = {"accounts": []}
    salt = os.urandom(SALT_SIZE)
    save_vault(password, vault, salt, filename)
    print("Vault created successfully.")

    return vault, salt, password


def add_entry(vault: dict) -> None:
    site = input("Site: ").strip()
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")

    if not site or not username or not password:
        print("Site, username, and password are required.")
        return

    vault["accounts"].append(
        {
            "site": site,
            "username": username,
            "password": password,
        }
    )
    print("Entry added.")


def list_entries(vault: dict) -> None:
    accounts = vault.get("accounts", [])
    if not accounts:
        print("No entries found.")
        return

    print("\nSaved entries:")
    for index, account in enumerate(accounts):
        print(f"{index}: {account['site']}")


def view_entry(vault: dict) -> None:
    accounts = vault.get("accounts", [])
    if not accounts:
        print("No entries found.")
        return

    list_entries(vault)

    try:
        index = int(input("Enter index to view: "))
    except ValueError:
        print("Invalid input.")
        return

    if index < 0 or index >= len(accounts):
        print("Invalid index.")
        return

    account = accounts[index]
    print("\n--- Entry ---")
    print(f"Site: {account['site']}")
    print(f"Username: {account['username']}")
    print(f"Password: {account['password']}")

    copy_choice = input("Copy password to clipboard? (y/n): ").strip().lower()
    if copy_choice in {"y", "yes"}:
        try:
            pyperclip.copy(account["password"])
            print("Password copied.")
        except pyperclip.PyperclipException:
            print("Clipboard is unavailable on this platform.")


def delete_entry(vault: dict) -> None:
    accounts = vault.get("accounts", [])

    if not accounts:
        print("No entries found.")
        return

    list_entries(vault)

    try:
        index = int(input("Enter index to delete: "))
    except ValueError:
        print("Invalid input.")
        return

    if index < 0 or index >= len(accounts):
        print("Invalid index.")
        return

    removed = accounts.pop(index)
    print(f"Removed entry for {removed['site']}")


def run_manager() -> None:
    if not os.path.exists(VAULT_FILE):
        vault, salt, master_password = create_vault(VAULT_FILE)
    else:
        master_password = getpass.getpass("Enter your master password: ")

        try:
            vault, salt = open_vault(master_password, VAULT_FILE)
            print("Vault unlocked.")
        except Exception:
            print("Failed to unlock vault. Please verify your password and try again.")
            return

    try:
        while True:
            print("\nOptions:")
            print("1. Add password")
            print("2. View entries")
            print("3. Delete entry")
            print("4. Generate password")
            print("5. Exit")

            choice = input("> ").strip()

            if choice == "1":
                add_entry(vault)
            elif choice == "2":
                view_entry(vault)
            elif choice == "3":
                delete_entry(vault)
            elif choice == "4":
                passwordgenerator.main()
            elif choice == "5":
                save_vault(master_password, vault, salt, VAULT_FILE)
                print("Vault saved. Goodbye.")
                break
            else:
                print("Invalid option. Please choose a number from 1 to 5.")
    except KeyboardInterrupt:
        print("\nGoodbye.")
        save_vault(master_password, vault, salt, VAULT_FILE)


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
        

        


#first time users get asked for master password
#write to the vault file 
#encrypt vault file 
def create_vault(filename="vault.json"):
    print("No vault found. Creating new vault.")

    password = getpass.getpass("Create master password: ")
    confirm = getpass.getpass("Confirm master password: ")

    if password != confirm:
        print("Passwords don't match.")
        return None, None
    
    vault = {
        "accounts": []
    }

    salt = os.urandom(16)

    save_vault(password, vault, salt, filename)

    print("Vault created successfully.")

    return vault, salt

    

 

def open_vault(master_password: str , filename = "vault.json"):
    with open(filename,"r") as f:
        data = json.load(f)

    #gets salt nonce and ciphertext from vault file
    salt = bytes.fromhex(data["salt"])
    nonce = bytes.fromhex(data["nonce"])
    ciphertext = bytes.fromhex(data["ciphertext"])
    
    key = derive_key(master_password, salt)
    aesgcm = AESGCM(key)

    plaintext = aesgcm.decrypt(nonce, ciphertext, None)

    vault = json.loads(plaintext.decode())
    
    return vault, salt


def save_vault(master_password: str, vault: dict, salt: bytes, filename="vault.json"):
    print("about to save vault")
    key = derive_key(master_password, salt)
    aesgcm = AESGCM(key)

    nonce = os.urandom(12)

    plaintext = json.dumps(vault).encode()
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    data = {
        "salt": salt.hex(),
        "nonce": nonce.hex(),
        "ciphertext": ciphertext.hex()
    }
    print("writing to file.")
    with open(filename,"w") as f:
        json.dump(data, f)
        print("file written")
    print("VAULT SAVED.")

    


def derive_key(password: str, salt: bytes)-> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200_000
    )

    return kdf.derive(password.encode())

print("Key derived successfully ")

