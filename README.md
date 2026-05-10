# TUI Password Manager

A terminal-based password manager that stores account credentials in a locally encrypted vault file.

## Features

- AES-GCM encrypted vault with PBKDF2 key derivation (200,000 iterations)
- Master password protection with strength enforcement
- Add, view, and delete password entries
- Secure password generation using Python's `secrets` module
- Clipboard support for copying passwords
- Specific error messages for wrong password, missing vault, and corrupt vault

## Installation

```bash
python -m pip install -r requirements.txt
```

## Usage

Run the password manager:

```bash
python passwordmanager.py
```

Generate a secure password without opening the vault:

```bash
python passwordmanager.py --generate
```

On first run, you will be prompted to create a master password. It must be at least 16 characters and include uppercase, lowercase, digits, and a special character.

### Example: creating a vault for the first time

```
$ python passwordmanager.py

No vault found. Creating a new vault.
Create master password:
Confirm master password:
Vault created successfully.

Options:
1. Add password
2. View entries
3. Delete entry
4. Generate password
5. Exit
> 1
Site: github.com
Username: myuser@example.com
Password:
Entry added.

Options:
...
> 5
Vault saved. Goodbye.
```

The password prompt does not echo characters to the terminal. Your vault is saved to `vault.json` in the current directory.

## Project structure

```
tuipasswordmanager/
├── passwordmanager.py   # Entry point — master password handling and orchestration
├── cli.py               # Interactive menu loop
├── vault.py             # Encryption (CryptoService), vault data model (Vault), persistence (VaultService)
├── passwordgenerator.py # Secure password generator
└── tests/
    ├── test_logic.py    # Unit tests for crypto, vault, and password generation
    └── test_cli.py      # Integration tests for the CLI menu
```

## Vault format and security

The vault is stored in `vault.json` as a JSON object with three fields:

```json
{
  "salt": "<hex>",
  "nonce": "<hex>",
  "ciphertext": "<hex>"
}
```

- The **salt** (16 bytes, random per vault creation) is passed to PBKDF2-HMAC-SHA256 with 200,000 iterations to derive a 256-bit AES key from the master password.
- The **nonce** (12 bytes, random per save) and **ciphertext** are produced by AES-GCM encryption of the JSON vault contents.
- The plaintext is never written to disk. An incorrect password or any modification to the ciphertext will cause decryption to fail with an authentication error.

> **Do not commit `vault.json` to source control.** It contains your encrypted passwords. The file is already listed in `.gitignore`, but if you ever move or rename it, make sure the new path is ignored too:
> ```
> vault.json
> ```

## Testing

```bash
pytest tests/
```

Use `-v` for per-test output:

```bash
pytest tests/ -v
```

## Security notice

This project is intended for learning purposes and should not replace a production password manager. Always keep your master password safe and keep a backup of your encrypted `vault.json`.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
