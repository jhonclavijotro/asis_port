import os
import json
import base64
from typing import Dict, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class VaultManager:
    """
    Gestor de Bóveda Portable Segura.
    Encripta y desencripta claves API y tokens OAuth usando Fernet (AES-256)
    con derivación de clave mediante PBKDF2HMAC a partir de una Contraseña Maestra.
    """

    DEFAULT_SALT = b"portable_agent_secure_salt_v1"

    def __init__(self, vault_filepath: str, master_passphrase: str):
        self.vault_filepath = os.path.abspath(vault_filepath)
        self._fernet = self._derive_fernet_key(master_passphrase)
        self._secrets: Dict[str, str] = {}
        self._load_vault()

    def _derive_fernet_key(self, passphrase: str) -> Fernet:
        """Deriva una clave de cifrado Fernet a partir de la frase de paso."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.DEFAULT_SALT,
            iterations=100_000,
        )
        derived_key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode("utf-8")))
        return Fernet(derived_key)

    def _load_vault(self) -> None:
        """Carga y desencripta el archivo de bóveda si existe."""
        if not os.path.exists(self.vault_filepath):
            self._secrets = {}
            return

        try:
            with open(self.vault_filepath, "rb") as f:
                encrypted_data = f.read()

            if not encrypted_data:
                self._secrets = {}
                return

            decrypted_data = self._fernet.decrypt(encrypted_data)
            self._secrets = json.loads(decrypted_data.decode("utf-8"))
        except Exception as e:
            raise ValueError(
                "No se pudo desencriptar la bóveda. "
                "Asegúrate de que la Contraseña Maestra sea correcta o que el archivo no esté dañado."
            ) from e

    def save_vault(self) -> None:
        """Encripta y guarda los secretos en el archivo de la bóveda."""
        os.makedirs(os.path.dirname(self.vault_filepath), exist_ok=True)
        json_data = json.dumps(self._secrets).encode("utf-8")
        encrypted_data = self._fernet.encrypt(json_data)

        with open(self.vault_filepath, "wb") as f:
            f.write(encrypted_data)

    def set_secret(self, key: str, value: str) -> None:
        """Guarda o actualiza un secreto en la bóveda."""
        self._secrets[key] = value
        self.save_vault()

    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Obtiene un secreto desencriptado."""
        return self._secrets.get(key, default)

    def delete_secret(self, key: str) -> bool:
        """Elimina un secreto de la bóveda."""
        if key in self._secrets:
            del self._secrets[key]
            self.save_vault()
            return True
        return False

    def list_keys(self) -> list[str]:
        """Devuelve la lista de claves almacenadas (sin exponer los valores)."""
        return list(self._secrets.keys())
