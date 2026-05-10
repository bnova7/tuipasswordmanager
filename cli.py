
from getpass import getpass
import pyperclip
import passwordgenerator
from vault import Vault, VaultService


def run_cli(vault: Vault, master_password: str, salt: bytes, vault_service: VaultService) -> None:
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
                site = input("Site: ").strip()
                username = input("Username: ").strip()
                password = getpass("Password: ")
                try:
                    vault.add_entry(site, username, password)
                    print("Entry added.")
                except ValueError as e:
                    print(e)
            elif choice == "2":
                accounts = vault.list_entries()
                if accounts:
                    print("\nSaved entries:")
                    for index, account in enumerate(accounts):
                        print(f"{index}: {account['site']}")
                else:
                    print("No entries found.")

                if accounts:
                    try:
                        index = int(input("Enter index to view: "))
                        entry = vault.get_entry(index)
                        if entry:
                            print("\n--- Entry ---")
                            print(f"Site: {entry['site']}")
                            print(f"Username: {entry['username']}")
                            print(f"Password: {entry['password']}")

                            copy_choice = input("Copy password to clipboard? (y/n): ").strip().lower()
                            if copy_choice in {"y", "yes"}:
                                try:
                                    pyperclip.copy(entry["password"])
                                    print("Password copied.")
                                except pyperclip.PyperclipException:
                                    print("Clipboard is unavailable on this platform.")
                        else:
                            print("Invalid index.")
                    except ValueError:
                        print("Invalid input.")
            elif choice == "3":
                accounts = vault.list_entries()
                if accounts:
                    print("\nSaved entries:")
                    for index, account in enumerate(accounts):
                        print(f"{index}: {account['site']}")
                else:
                    print("No entries found.")

                if accounts:
                    try:
                        index = int(input("Enter index to delete: "))
                        removed = vault.delete_entry(index)
                        print(f"Removed entry for {removed['site']}")
                    except (ValueError, IndexError) as e:
                        print(e)
            elif choice == "4":
                passwordgenerator.main()
            elif choice == "5":
                vault_service.save_vault(master_password, vault, salt)
                print("Vault saved. Goodbye.")
                break
            else:
                print("Invalid option. Please choose a number from 1 to 5.")
    except KeyboardInterrupt:
        vault_service.save_vault(master_password, vault, salt)
        print("\nVault saved. Goodbye.")