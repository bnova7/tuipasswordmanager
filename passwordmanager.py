import argparse
import getpass
import os
import passwordgenerator
from vault import CryptoService, Vault, VaultService


VAULT_FILE = "vault.json"


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
            print("Password cannot be empty. Please try again.")
            return get_password(prompt, validate_strength)

        if validate_strength and not check_password_strength(password):
            print("Password is too weak. It must be at least 16 characters long and include uppercase, lowercase, digits, and special characters.")
            return get_password(prompt, validate_strength)

        return password
    except KeyboardInterrupt:
        print("\nGoodbye.")
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
        print("\nGoodbye.")
        exit(0)


def get_master_password() -> str:
    return get_password("Enter master password: ")


def run_manager() -> None:
    vault_service = VaultService(CryptoService())

    if not vault_service.vault_exists():
        print("No vault found. Creating a new vault.")
        master_password = get_master_password_confirm()
        vault, salt = vault_service.create_vault(master_password)
        print("Vault created successfully.")
    else:
        master_password = get_master_password()

        try:
            vault, salt = vault_service.load_vault(master_password)
            print("Vault unlocked.")
        except Exception:
            print("Failed to unlock vault. Please verify your password and try again.")
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

    



