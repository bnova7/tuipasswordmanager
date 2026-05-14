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

- The **salt** (16 bytes, randomly generated at vault creation) is fed into PBKDF2-HMAC-SHA256 with 200,000 iterations to derive a 256-bit AES key from the master password. The salt never changes after creation.
- The **nonce** (12 bytes) is randomly regenerated on every save, so each write produces a unique ciphertext even if the vault contents are unchanged.
- The **ciphertext** is the AES-GCM encryption of the plaintext vault contents. AES-GCM appends a 16-byte authentication tag to the ciphertext — any modification to the ciphertext, nonce, or salt will cause decryption to fail with an authentication error.
- The master password never touches disk. It is used transiently in memory to derive the AES key and is not stored anywhere in the vault file.

The plaintext inside the vault is a JSON object with this structure:

```json
{
  "accounts": [
    {"site": "example.com", "username": "user@example.com", "password": "..."}
  ]
}
```

**Security assumptions:**
- The master password is the only secret. Anyone with the `vault.json` file cannot decrypt it without the master password.
- A wrong password or any byte-level tampering with the vault file will raise a decryption error — there is no silent data corruption.
- The derived AES key exists only in memory for the duration of the session and is never persisted.

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
