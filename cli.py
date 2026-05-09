
from getpass import getpass
import pyperclip
import passwordgenerator
from passwordmanager import save_vault, add_entry, list_entries, get_entry, delete_entry


def run_cli(vault: dict, master_password: str, salt: bytes) -> None:
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
                    add_entry(vault, site, username, password)
                    print("Entry added.")
                except ValueError as e:
                    print(e)
            elif choice == "2":
                list_entries(vault)
                if vault.get("accounts"):
                    try:
                        index = int(input("Enter index to view: "))
                        entry = get_entry(vault, index)
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
                list_entries(vault)
                if vault.get("accounts"):
                    try:
                        index = int(input("Enter index to delete: "))
                        removed = delete_entry(vault, index)
                        print(f"Removed entry for {removed['site']}")
                    except (ValueError, IndexError) as e:
                        print(e)
            elif choice == "4":
                passwordgenerator.main()
            elif choice == "5":
                save_vault(master_password, vault, salt)
                print("Vault saved. Goodbye.")
                break
            else:
                print("Invalid option. Please choose a number from 1 to 5.")
    except KeyboardInterrupt:
        save_vault(master_password, vault, salt)
        print("\nVault saved. Goodbye.")