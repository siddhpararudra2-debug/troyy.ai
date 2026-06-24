"""
Sprint 12 — Secret Manager
Secrets storage, rotation policies, and vault integration abstraction.
"""
from __future__ import annotations

import base64
import hashlib
import logging
import secrets
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class SecretType(str, Enum):
    API_KEY = "api_key"
    DATABASE_CREDENTIAL = "database_credential"
    TLS_CERTIFICATE = "tls_certificate"
    OAUTH_TOKEN = "oauth_token"
    SSH_KEY = "ssh_key"
    GENERIC = "generic"
    ENCRYPTION_KEY = "encryption_key"


class SecretStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    ROTATING = "rotating"


@dataclass
class SecretRecord:
    """A managed secret."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    secret_type: SecretType = SecretType.GENERIC
    encrypted_value: str = ""  # Base64-encoded encrypted value
    version: int = 1
    status: SecretStatus = SecretStatus.ACTIVE
    tenant_id: str = "default"
    namespace: str = "default"
    rotation_days: Optional[int] = None
    last_rotated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    access_log: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def is_rotation_due(self) -> bool:
        if not self.rotation_days or not self.last_rotated_at:
            return False
        return datetime.now(timezone.utc) > self.last_rotated_at + timedelta(days=self.rotation_days)

    def to_dict(self, include_value: bool = False) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "secret_type": self.secret_type.value,
            "version": self.version,
            "status": self.status.value,
            "tenant_id": self.tenant_id,
            "namespace": self.namespace,
            "rotation_days": self.rotation_days,
            "rotation_due": self.is_rotation_due,
            "last_rotated_at": self.last_rotated_at.isoformat() if self.last_rotated_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            **({"encrypted_value": self.encrypted_value} if include_value else {}),
        }


class SecretManager:
    """
    Manages secrets with encryption at rest, versioning, and rotation policies.
    HashiCorp Vault-ready abstraction layer.
    """

    def __init__(self, master_key: Optional[str] = None):
        self._master_key = master_key or secrets.token_hex(32)
        self._secrets: Dict[str, SecretRecord] = {}
        self._access_policies: Dict[str, List[str]] = {}  # tenant -> accessible secret IDs

    def _encrypt(self, value: str) -> str:
        """Simulate encryption (in production: use AES-256-GCM via cryptography library)."""
        key_hash = hashlib.sha256(self._master_key.encode()).digest()
        encoded = base64.b64encode(value.encode()).decode()
        signature = hashlib.hmac_new(
            key_hash, encoded.encode(), hashlib.sha256
        ).hexdigest()[:8] if hasattr(hashlib, 'hmac_new') else hashlib.sha256(encoded.encode() + key_hash).hexdigest()[:8]
        return f"enc:{encoded}:{signature}"

    def _decrypt(self, encrypted: str) -> str:
        """Simulate decryption."""
        if encrypted.startswith("enc:"):
            parts = encrypted.split(":")
            if len(parts) >= 2:
                return base64.b64decode(parts[1]).decode()
        return encrypted

    async def create_secret(
        self,
        name: str,
        value: str,
        secret_type: SecretType = SecretType.GENERIC,
        tenant_id: str = "default",
        namespace: str = "default",
        rotation_days: Optional[int] = None,
        expires_in_days: Optional[int] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> SecretRecord:
        """Create and store a new secret."""
        secret = SecretRecord(
            name=name,
            secret_type=secret_type,
            encrypted_value=self._encrypt(value),
            tenant_id=tenant_id,
            namespace=namespace,
            rotation_days=rotation_days,
            last_rotated_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=expires_in_days) if expires_in_days else None,
            tags=tags or {},
        )
        self._secrets[secret.id] = secret
        logger.info(f"Secret '{name}' [{secret_type.value}] created for tenant '{tenant_id}'")
        return secret

    async def get_secret(
        self, secret_id: str, tenant_id: str = "default", requester: str = "system"
    ) -> Optional[str]:
        """Retrieve a secret value (decrypted)."""
        secret = self._secrets.get(secret_id)
        if not secret or secret.tenant_id != tenant_id:
            return None
        if secret.status in (SecretStatus.REVOKED, SecretStatus.EXPIRED):
            raise ValueError(f"Secret '{secret.name}' is {secret.status.value}")

        # Log access
        secret.access_log.append({
            "requester": requester,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return self._decrypt(secret.encrypted_value)

    async def rotate_secret(
        self, secret_id: str, new_value: str, tenant_id: str = "default"
    ) -> SecretRecord:
        """Rotate a secret to a new value."""
        secret = self._secrets.get(secret_id)
        if not secret or secret.tenant_id != tenant_id:
            raise ValueError(f"Secret {secret_id} not found")

        secret.status = SecretStatus.ROTATING
        secret.encrypted_value = self._encrypt(new_value)
        secret.version += 1
        secret.last_rotated_at = datetime.now(timezone.utc)
        secret.status = SecretStatus.ACTIVE
        secret.updated_at = datetime.now(timezone.utc)
        logger.info(f"Secret '{secret.name}' rotated to version {secret.version}")
        return secret

    async def revoke_secret(self, secret_id: str, tenant_id: str = "default") -> SecretRecord:
        """Revoke a secret."""
        secret = self._secrets.get(secret_id)
        if not secret or secret.tenant_id != tenant_id:
            raise ValueError(f"Secret {secret_id} not found")
        secret.status = SecretStatus.REVOKED
        secret.updated_at = datetime.now(timezone.utc)
        logger.warning(f"Secret '{secret.name}' REVOKED")
        return secret

    async def list_secrets(
        self,
        tenant_id: Optional[str] = None,
        namespace: Optional[str] = None,
        secret_type: Optional[SecretType] = None,
        rotation_due_only: bool = False,
    ) -> List[SecretRecord]:
        secrets = list(self._secrets.values())
        if tenant_id:
            secrets = [s for s in secrets if s.tenant_id == tenant_id]
        if namespace:
            secrets = [s for s in secrets if s.namespace == namespace]
        if secret_type:
            secrets = [s for s in secrets if s.secret_type == secret_type]
        if rotation_due_only:
            secrets = [s for s in secrets if s.is_rotation_due]
        return secrets

    async def audit_rotation_needed(self) -> List[Dict[str, Any]]:
        """Return all secrets due for rotation."""
        due = [s for s in self._secrets.values() if s.is_rotation_due and s.status == SecretStatus.ACTIVE]
        return [{"secret_id": s.id, "name": s.name, "last_rotated": s.last_rotated_at.isoformat() if s.last_rotated_at else None} for s in due]

    def get_secret_summary(self) -> Dict[str, Any]:
        secrets = list(self._secrets.values())
        return {
            "total_secrets": len(secrets),
            "by_status": {s.value: sum(1 for sec in secrets if sec.status == s) for s in SecretStatus},
            "rotation_due": sum(1 for s in secrets if s.is_rotation_due),
            "by_type": {t.value: sum(1 for s in secrets if s.secret_type == t) for t in SecretType},
        }
