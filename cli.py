
from getpass import getpass
import rich 
import pyperclip
import threading 
from rich.panel import Panel
import passwordgenerator
from vault import Vault, VaultService



def print_entries(vault: Vault ) -> list:
                accounts = vault.list_entries()
                if accounts:
                    rich.print("\n[bold]Saved entries:[/bold]")
                    for index, account in enumerate(accounts):
                        rich.print(f"[cyan]{index}: {account['site']}[/cyan]")
                else:
                    rich.print("[red]No entries found.[/red]")

                return accounts 
                
#copies text starts a timer to clear the clipboard
def copy_with_autoclean(text, timeout=30):
    pyperclip.copy(text)
    timer = threading.Timer(timeout, pyperclip.copy, args=[""])
    timer.start()
    return timer

def search_entries(vault, query):
    """Search for entries matching the query."""
    results = []
    for index, entry in enumerate(vault.list_entries()):
        if query.lower() in entry["site"].lower() or query.lower() in entry["username"].lower():
            results.append((index, entry))
    return results

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
            new_password = getpass("New password (leave blank to keep current): ")
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
            exit(0)

def run_cli(vault: Vault, master_password: str, salt: bytes, vault_service: VaultService) -> None:
    try:
        while True:
            rich.print(Panel.fit("[bold green]Password Manager[/bold green]", title="Main Menu", border_style="green"))
            rich.print("[yellow]1. Add entry[/yellow]")
            rich.print("[yellow]2. View entries[/yellow]")
            rich.print("[yellow]3. Delete entry[/yellow]")
            rich.print("[yellow]4. Generate password[/yellow]")
            rich.print("[yellow]5. Save and exit[/yellow]")
            rich.print("[yellow]6. Search entries[/yellow]")
            rich.print("[yellow]7. Edit entry[/yellow]")

            choice = input("> ").strip()

            if choice == "1":
                site = input("Site: ").strip()
                username = input("Username: ").strip()
                password = getpass("Password: ")
                try:
                    vault.add_entry(site, username, password)
                    vault_service.save_vault(master_password, vault, salt)
                    rich.print("[green]Entry added.[/green]")
                    rich.print("[green]Vault saved.[/green]")
                except ValueError as e:
                    rich.print(f"[red]{e}[/red]")
            elif choice == "2":
                accounts = print_entries(vault)
                if accounts:
                    try:
                        index = int(input("Enter index to view: "))
                        entry = vault.get_entry(index)
                        if entry:
                            rich.print("\n[bold]--- Entry ---[/bold]")
                            rich.print(f"[cyan]Site: {entry['site']}[/cyan]")
                            rich.print(f"[cyan]Username: {entry['username']}[/cyan]")
                            rich.print(f"[cyan]Password: {entry['password']}[/cyan]")

                            copy_choice = input("Copy password to clipboard? (y/n): ").strip().lower()
                            if copy_choice in {"y", "yes"}:
                                try:
                                    copy_with_autoclean(entry["password"], timeout=30)
                                    rich.print("[green]Password copied. Clipboard will be cleared in 30 seconds.[/green]")
                                except pyperclip.PyperclipException:
                                    rich.print("[red]Clipboard is unavailable on this platform. On linux, install xclip, xsel, or wl-clipboard.[/red]")
                        else:
                            rich.print("[red]Invalid index.[/red]")
                    except ValueError:
                        rich.print("[red]Invalid input.[/red]")
            elif choice == "3":
                accounts = print_entries(vault)
                if accounts:
                    try:
                        index = int(input("Enter index to delete: "))
                        removed = vault.delete_entry(index)
                        vault_service.save_vault(master_password, vault, salt)
                        rich.print(f"[green]Removed entry for {removed['site']}[/green]")
                        rich.print("[green]Vault saved.[/green]")
                    except (ValueError, IndexError) as e:
                        rich.print(f"[red]{e}[/red]")
            elif choice == "4":
                passwordgenerator.main()
            elif choice == "5":
                vault_service.save_vault(master_password, vault, salt)
                rich.print("[green]Vault saved. Goodbye.[/green]")
                break
            elif choice == "6":
                query = input("Enter search query: ").strip()
                results = search_entries(vault, query)
                if results:
                    rich.print("\n[bold]Search results:[/bold]")
                    for index, entry in results:
                        rich.print(f"[cyan]{index}: {entry['site']} ({entry['username']})[/cyan]")
                else:
                    rich.print("[red]No matching entries found.[/red]")
            elif choice == "7":
                try:
                    accounts = print_entries(vault)
                    index = int(input("Enter index to edit: "))
                    edit_entry(vault, index, master_password, salt, vault_service)
                except (ValueError, IndexError):
                    rich.print("[red]Invalid index.[/red]")
            else:
                rich.print("[red]Invalid option. Please choose a number from 1 to 7.[/red]")
    except KeyboardInterrupt:
        vault_service.save_vault(master_password, vault, salt)
        rich.print("\n[green]Vault saved. Goodbye.[/green]")