"""
Sprint 12 — Encryption Engine
AES-256 encryption for data at rest with key derivation and management.
"""
from __future__ import annotations

import base64
import hashlib
import logging
import os
import secrets
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class EncryptionAlgorithm(str, Enum):
    AES_256_GCM = "AES-256-GCM"
    AES_256_CBC = "AES-256-CBC"
    CHACHA20_POLY1305 = "ChaCha20-Poly1305"
    RSA_4096 = "RSA-4096"


class KeyPurpose(str, Enum):
    DATA_AT_REST = "data_at_rest"
    DATA_IN_TRANSIT = "data_in_transit"
    KEY_ENCRYPTION = "key_encryption"
    SIGNING = "signing"
    AUTHENTICATION = "authentication"


@dataclass
class EncryptionKey:
    """An encryption key record."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    purpose: KeyPurpose = KeyPurpose.DATA_AT_REST
    key_material: str = ""  # Base64-encoded (never expose in API)
    key_hash: str = ""      # SHA-256 of key (for identification)
    version: int = 1
    is_active: bool = True
    tenant_id: str = "default"
    rotation_days: int = 90
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "algorithm": self.algorithm.value,
            "purpose": self.purpose.value,
            "key_hash": self.key_hash,
            "version": self.version,
            "is_active": self.is_active,
            "tenant_id": self.tenant_id,
            "rotation_days": self.rotation_days,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class EncryptedData:
    """Result of an encryption operation."""
    ciphertext: str = ""    # Base64-encoded
    iv: str = ""            # Base64-encoded initialization vector
    auth_tag: str = ""      # Authentication tag for AEAD
    key_id: str = ""
    algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    encrypted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ciphertext": self.ciphertext,
            "iv": self.iv,
            "auth_tag": self.auth_tag,
            "key_id": self.key_id,
            "algorithm": self.algorithm.value,
        }


class EncryptionEngine:
    """
    AES-256-GCM encryption engine with key management for data at rest.
    Simulates actual cryptographic operations for integration compatibility.
    In production: integrate with `cryptography` library or cloud KMS.
    """

    def __init__(self):
        self._keys: Dict[str, EncryptionKey] = {}
        self._key_by_name: Dict[str, str] = {}  # name -> key_id
        self._encryption_stats = {"encrypted": 0, "decrypted": 0, "keys_created": 0}

    async def generate_key(
        self,
        name: str,
        algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM,
        purpose: KeyPurpose = KeyPurpose.DATA_AT_REST,
        rotation_days: int = 90,
        tenant_id: str = "default",
    ) -> EncryptionKey:
        """Generate a new encryption key."""
        key_bytes = os.urandom(32)  # 256-bit key
        key_material = base64.b64encode(key_bytes).decode()
        key_hash = hashlib.sha256(key_bytes).hexdigest()

        key = EncryptionKey(
            name=name,
            algorithm=algorithm,
            purpose=purpose,
            key_material=key_material,
            key_hash=key_hash,
            rotation_days=rotation_days,
            tenant_id=tenant_id,
        )
        self._keys[key.id] = key
        self._key_by_name[name] = key.id
        self._encryption_stats["keys_created"] += 1
        logger.info(f"Encryption key '{name}' generated ({algorithm.value}) for tenant '{tenant_id}'")
        return key

    async def encrypt(
        self,
        plaintext: bytes,
        key_id: str,
        additional_data: Optional[bytes] = None,
    ) -> EncryptedData:
        """Encrypt data using the specified key (AES-256-GCM simulation)."""
        key = self._keys.get(key_id)
        if not key or not key.is_active:
            raise ValueError(f"Key {key_id} not found or not active")

        # Simulate AES-256-GCM encryption
        iv = os.urandom(12)  # 96-bit GCM nonce
        key_bytes = base64.b64decode(key.key_material)

        # XOR with key for simulation (real code would use AES-256-GCM)
        padded = plaintext + b"\0" * (16 - len(plaintext) % 16)
        ciphertext = bytes(a ^ b for a, b in zip(padded, key_bytes * (len(padded) // 32 + 1)))
        auth_tag = hashlib.sha256(ciphertext + iv + (additional_data or b"")).digest()[:16]

        result = EncryptedData(
            ciphertext=base64.b64encode(ciphertext).decode(),
            iv=base64.b64encode(iv).decode(),
            auth_tag=base64.b64encode(auth_tag).decode(),
            key_id=key_id,
            algorithm=key.algorithm,
        )
        self._encryption_stats["encrypted"] += 1
        return result

    async def decrypt(
        self,
        encrypted: EncryptedData,
        additional_data: Optional[bytes] = None,
    ) -> bytes:
        """Decrypt data using the key referenced in the encrypted payload."""
        key = self._keys.get(encrypted.key_id)
        if not key:
            raise ValueError(f"Key {encrypted.key_id} not found")

        key_bytes = base64.b64decode(key.key_material)
        ciphertext = base64.b64decode(encrypted.ciphertext)

        # Simulate decryption (reverse XOR)
        plaintext = bytes(a ^ b for a, b in zip(ciphertext, key_bytes * (len(ciphertext) // 32 + 1)))
        self._encryption_stats["decrypted"] += 1
        return plaintext.rstrip(b"\0")

    async def rotate_key(self, key_id: str) -> Tuple[EncryptionKey, EncryptionKey]:
        """Rotate an encryption key, keeping the old one for decryption."""
        old_key = self._keys.get(key_id)
        if not old_key:
            raise ValueError(f"Key {key_id} not found")

        old_key.is_active = False
        new_key = await self.generate_key(
            name=old_key.name,
            algorithm=old_key.algorithm,
            purpose=old_key.purpose,
            rotation_days=old_key.rotation_days,
            tenant_id=old_key.tenant_id,
        )
        new_key.version = old_key.version + 1
        self._key_by_name[old_key.name] = new_key.id
        logger.info(f"Key '{old_key.name}' rotated to version {new_key.version}")
        return old_key, new_key

    async def encrypt_string(self, text: str, key_id: str) -> str:
        """Convenience: encrypt a string and return base64 ciphertext string."""
        result = await self.encrypt(text.encode(), key_id)
        return f"{result.iv}:{result.ciphertext}:{result.auth_tag}:{result.key_id}"

    async def decrypt_string(self, encrypted_str: str) -> str:
        """Convenience: decrypt a string from encrypt_string format."""
        parts = encrypted_str.split(":")
        if len(parts) != 4:
            raise ValueError("Invalid encrypted string format")
        iv, ciphertext, auth_tag, key_id = parts
        encrypted = EncryptedData(
            ciphertext=ciphertext, iv=iv, auth_tag=auth_tag, key_id=key_id
        )
        return (await self.decrypt(encrypted)).decode()

    async def get_key(self, key_id: str) -> Optional[EncryptionKey]:
        return self._keys.get(key_id)

    async def list_keys(
        self,
        tenant_id: Optional[str] = None,
        purpose: Optional[KeyPurpose] = None,
        active_only: bool = True,
    ) -> List[EncryptionKey]:
        keys = list(self._keys.values())
        if tenant_id:
            keys = [k for k in keys if k.tenant_id == tenant_id]
        if purpose:
            keys = [k for k in keys if k.purpose == purpose]
        if active_only:
            keys = [k for k in keys if k.is_active]
        return keys

    def get_encryption_stats(self) -> Dict[str, Any]:
        return {
            "total_keys": len(self._keys),
            "active_keys": sum(1 for k in self._keys.values() if k.is_active),
            **self._encryption_stats,
        }
