import secrets
import string
import pyperclip
import rich 

def generate_password(length: int = 16) -> str:
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def copy_to_clipboard(value: str) -> None:
    """Copy text to the clipboard, if available."""
    try:
        pyperclip.copy(value)
    except pyperclip.PyperclipException:
        print("Warning: clipboard is not available on this platform.")


def main() -> None:
    try:
        password = generate_password()
        rich.print(f"[cyan]Generated password: {password}[/cyan]")
        choice = input("Copy password? (y/n): ").strip().lower()

        if choice in {"y", "yes"}:
            copy_to_clipboard(password)
            rich.print("[green]Password copied to clipboard.[/green]")

    except KeyboardInterrupt:
        rich.print("\n[green]Goodbye.[/green]")

if __name__ == "__main__":
    main()







