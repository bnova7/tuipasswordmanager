import argparse
import getpass
import json

import rich
import passwordgenerator
from cryptography.exceptions import InvalidTag
from vault import CryptoService, VaultService


VAULT_FILE = "vault.json"
def edit_entry(vault, index, master_password, salt, vault_service):
        try:
            entry = vault.get_entry(index)
            if not entry:
                print("Invalid index.")
                return
            rich.print("[green]\n--- Edit Entry ---[/green]")
            rich.print(f"[green]Current site: {entry['site']}[/green]")
            new_site = input("New site (leave blank to keep current): ").strip()
            rich.print(f"[green]Current username: {entry['username']}[/green]")
            new_username = input("New username (leave blank to keep current): ").strip()
            new_password = get_password("New password (leave blank to keep current): ", validate_strength=True)
            if new_site:
                entry['site'] = new_site
            if new_username:
                entry['username'] = new_username
            if new_password:
                entry['password'] = new_password
            vault_service.save_vault(master_password, vault, salt)
            rich.print("[green]Vault saved.[/green]")

        except KeyboardInterrupt:
            rich.print("\n[green]Goodbye.[/green]")


def search_entries(vault, query):
    """Search for entries matching the query."""
    results = []
    for index, entry in enumerate(vault.list_entries()):
        if query.lower() in entry["site"].lower() or query.lower() in entry["username"].lower():
            results.append((index, entry))
    return results

def check_password_strength(password: str) -> bool:
    """Basic password strength check."""
    if len(password) < 16:
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


def get_password(prompt: str, validate_strength: bool = False) -> str:
    """Get password from user with optional strength validation."""
    try:
        password = getpass.getpass(prompt)
        if not password:
            if password == "":
                return
            print("Password cannot be empty. Please try again.")
            return get_password(prompt, validate_strength)

        if validate_strength and not check_password_strength(password):
            print("Password is too weak. It must be at least 16 characters long and include uppercase, lowercase, digits, and special characters.")
            return get_password(prompt, validate_strength)

        return password
    except KeyboardInterrupt:
        rich.print("\n[green]Goodbye.[/green]")
        exit(0)


def get_master_password_confirm() -> str:
    try:
        password = get_password("Create master password: ", validate_strength=True)
        confirm_password = getpass.getpass("Confirm master password: ")

        if password != confirm_password:
            print("Passwords do not match. Please try again.")
            return get_master_password_confirm()

        return password
    except KeyboardInterrupt:
        rich.print("\n[green]Goodbye.[/green]")
        exit(0)


def get_master_password() -> str:
    try:
        return getpass.getpass("Enter master password: ")
    except KeyboardInterrupt:
        rich.print("\n[green]Goodbye.[/green]")
        exit(0)



def run_manager() -> None:
    vault_service = VaultService(CryptoService())

    if not vault_service.vault_exists():
        print("No vault found. Creating a new vault.")
        master_password = get_master_password_confirm()
        vault, salt = vault_service.create_vault(master_password)
        print("Vault created successfully.")
    else:
        for attempt in range(3):
            master_password = get_master_password()
            remaining = 2 - attempt
            if not master_password:
                if remaining > 0:
                    print(f"Password cannot be empty. {remaining} attempt(s) remaining.")
                else:
                    print("Too many failed attempts. Exiting.")
                    exit(1)
                continue
            try:
                vault, salt = vault_service.load_vault(master_password)
                print("Vault unlocked.")
                break
            except FileNotFoundError:
                print("Vault file not found. Please check that vault.json exists.")
                return
            except InvalidTag:
                if remaining > 0:
                    print(f"Wrong password. {remaining} attempt(s) remaining.")
                else:
                    print("Too many failed attempts. Exiting.")
                    exit(1)
            except (json.JSONDecodeError, KeyError, ValueError):
                print("Vault file is corrupted and cannot be read.")
                return
        else:
            return

    import cli
    cli.run_cli(vault, master_password, salt, vault_service)


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

    



