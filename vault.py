import os
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


VAULT_FILE = "vault.json"
SALT_SIZE = 16
NONCE_SIZE = 12
KDF_ITERATIONS = 200_000


class CryptoService:
    """Handles all cryptographic operations."""

    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=KDF_ITERATIONS,
        )
        return kdf.derive(password.encode())

    @staticmethod
    def encrypt_data(key: bytes, data: bytes) -> tuple[bytes, bytes]:
        aesgcm = AESGCM(key)
        nonce = os.urandom(NONCE_SIZE)
        ciphertext = aesgcm.encrypt(nonce, data, None)
        return nonce, ciphertext

    @staticmethod
    def decrypt_data(key: bytes, nonce: bytes, ciphertext: bytes) -> bytes:
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, None)


class Vault:
    """Represents the password vault data structure."""

    def __init__(self, accounts: list[dict] = None):
        self.accounts = accounts or []

    def add_entry(self, site: str, username: str, password: str) -> dict:
        if not site or not username or not password:
            raise ValueError("Site, username, and password are required.")
        entry = {"site": site, "username": username, "password": password}
        self.accounts.append(entry)
        return entry

    def get_entry(self, index: int) -> dict | None:
        for account in self.accounts:
            if account["site"] == index:
                print(account)
        if 0 <= index < len(self.accounts):
            return self.accounts[index]
        return None

    def delete_entry(self, index: int) -> dict:
        if not (0 <= index < len(self.accounts)):
            raise IndexError("Invalid index.")
        return self.accounts.pop(index)

    def list_entries(self) -> list[dict]:
        return self.accounts

    def to_dict(self) -> dict:
        return {"accounts": self.accounts}

    @classmethod
    def from_dict(cls, data: dict) -> 'Vault':
        return cls(data.get("accounts", []))


class VaultService:
    """Handles vault persistence and loading."""

    def __init__(self, crypto: CryptoService, vault_file: str = VAULT_FILE):
        self.crypto = crypto
        self.vault_file = vault_file

    def save_vault(self, master_password: str, vault: Vault, salt: bytes) -> None:
        key = self.crypto.derive_key(master_password, salt)
        data = json.dumps(vault.to_dict(), separators=(",", ":")).encode()
        nonce, ciphertext = self.crypto.encrypt_data(key, data)

        vault_data = {
            "salt": salt.hex(),
            "nonce": nonce.hex(),
            "ciphertext": ciphertext.hex(),
        }

        with open(self.vault_file, "w", encoding="utf-8") as f:
            json.dump(vault_data, f)

    def load_vault(self, master_password: str) -> tuple[Vault, bytes]:
        with open(self.vault_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        salt = bytes.fromhex(data["salt"])
        nonce = bytes.fromhex(data["nonce"])
        ciphertext = bytes.fromhex(data["ciphertext"])

        key = self.crypto.derive_key(master_password, salt)
        plaintext = self.crypto.decrypt_data(key, nonce, ciphertext)
        vault_data = json.loads(plaintext.decode())

        return Vault.from_dict(vault_data), salt

    def vault_exists(self) -> bool:
        return os.path.exists(self.vault_file)

    def create_vault(self, master_password: str) -> tuple[Vault, bytes]:
        vault = Vault()
        salt = os.urandom(SALT_SIZE)
        self.save_vault(master_password, vault, salt)
        return vault, salt