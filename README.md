# TUI Password Manager

A simple terminal-based password manager that stores account credentials in a locally encrypted vault.

## Features

- AES-GCM encrypted vault file
- Master password protection
- Add, view, delete password entries
- Password generation and clipboard support
- Minimal dependencies and simple command-line interface

## Installation

```bash
python -m pip install -r requirements.txt
```

## Usage

Run the vault manager:

```bash
python passwordmanager.py
```

Generate a secure password directly:

```bash
python passwordmanager.py --generate
```

## Testing

This project uses `pytest` for automated tests.

Install pytest if needed:

```bash
python -m pip install pytest
```

Run the test suite:

```bash
pytest tests/
```

If you want more detail, use verbose mode:

```bash
pytest tests/ -v
```

## Vault behavior

- The vault is stored in `vault.json`
- A new vault is created automatically if the file does not exist
- Only encrypted data is written to disk
- Do not commit `vault.json` to source control

## Project structure

- `passwordmanager.py` — main vault application
- `passwordgenerator.py` — secure password generator
- `requirements.txt` — runtime dependencies
- `LICENSE` — project license

## Recommendations for professionalism

- Add tests for generator and vault functionality
- Use a package layout and `pyproject.toml` for installation
- Add `.gitignore` to exclude local secrets and cache files
- Keep sensitive data out of version control

## Security notice

This project is intended for learning and should not replace a production password manager.
Always keep your master password safe and backup your encrypted vault file.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
