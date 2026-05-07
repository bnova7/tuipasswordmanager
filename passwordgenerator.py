import secrets
import string
import pyperclip

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
        print(password)
        choice = input("Copy password? (y/n): ").strip().lower()

        if choice in {"y", "yes"}:
            copy_to_clipboard(password)
            print("Password copied to clipboard.")

    except KeyboardInterrupt:
        print("\nGoodbye.")


if __name__ == "__main__":
    main()







