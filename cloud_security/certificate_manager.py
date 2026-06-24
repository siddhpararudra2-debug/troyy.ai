"""
Sprint 12 — Certificate Manager
TLS certificate lifecycle, generation, renewal, and ACME/Let's Encrypt integration stub.
"""
from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class CertificateStatus(str, Enum):
    VALID = "valid"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING_RENEWAL = "pending_renewal"
    PENDING_ISSUANCE = "pending_issuance"


class CertificateType(str, Enum):
    TLS = "tls"
    MTLS = "mtls"
    CODE_SIGNING = "code_signing"
    CA = "ca"


@dataclass
class Certificate:
    """A TLS/mTLS certificate record."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    common_name: str = ""
    san_domains: List[str] = field(default_factory=list)
    certificate_type: CertificateType = CertificateType.TLS
    status: CertificateStatus = CertificateStatus.PENDING_ISSUANCE
    issuer: str = "Let's Encrypt"
    serial_number: str = ""
    fingerprint: str = ""
    key_algorithm: str = "RSA-2048"
    tenant_id: str = "default"
    namespace: str = "default"
    cluster_id: str = ""
    pem_certificate: str = ""
    pem_private_key: str = ""
    issued_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    auto_renew: bool = True
    renewal_threshold_days: int = 30
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def days_until_expiry(self) -> Optional[int]:
        if not self.expires_at:
            return None
        delta = self.expires_at - datetime.now(timezone.utc)
        return max(0, delta.days)

    @property
    def renewal_due(self) -> bool:
        days = self.days_until_expiry
        return days is not None and days <= self.renewal_threshold_days

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "common_name": self.common_name,
            "san_domains": self.san_domains,
            "certificate_type": self.certificate_type.value,
            "status": self.status.value,
            "issuer": self.issuer,
            "serial_number": self.serial_number,
            "fingerprint": self.fingerprint,
            "tenant_id": self.tenant_id,
            "namespace": self.namespace,
            "issued_at": self.issued_at.isoformat() if self.issued_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "days_until_expiry": self.days_until_expiry,
            "renewal_due": self.renewal_due,
            "auto_renew": self.auto_renew,
        }


class CertificateManager:
    """
    TLS certificate lifecycle manager. Supports issuance, renewal, and revocation.
    ACME/Let's Encrypt integration ready.
    """

    def __init__(self, ca_url: str = "https://acme-v02.api.letsencrypt.org"):
        self._ca_url = ca_url
        self._certificates: Dict[str, Certificate] = {}

    async def issue_certificate(
        self,
        common_name: str,
        san_domains: Optional[List[str]] = None,
        certificate_type: CertificateType = CertificateType.TLS,
        validity_days: int = 90,
        key_algorithm: str = "RSA-2048",
        tenant_id: str = "default",
        namespace: str = "default",
        cluster_id: str = "",
        auto_renew: bool = True,
        issuer: str = "Let's Encrypt",
    ) -> Certificate:
        """Issue a new TLS certificate."""
        now = datetime.now(timezone.utc)
        serial = uuid.uuid4().hex[:16].upper()
        fingerprint = hashlib.sha256(f"{common_name}{serial}{now.isoformat()}".encode()).hexdigest()

        cert = Certificate(
            common_name=common_name,
            san_domains=san_domains or [common_name],
            certificate_type=certificate_type,
            status=CertificateStatus.VALID,
            issuer=issuer,
            serial_number=serial,
            fingerprint=fingerprint,
            key_algorithm=key_algorithm,
            tenant_id=tenant_id,
            namespace=namespace,
            cluster_id=cluster_id,
            auto_renew=auto_renew,
            issued_at=now,
            expires_at=now + timedelta(days=validity_days),
            # Simulated PEM content
            pem_certificate=f"-----BEGIN CERTIFICATE-----\n{fingerprint[:64]}\n-----END CERTIFICATE-----",
            pem_private_key=f"-----BEGIN PRIVATE KEY-----\n{serial}\n-----END PRIVATE KEY-----",
        )
        self._certificates[cert.id] = cert
        logger.info(f"Certificate issued for '{common_name}' (valid {validity_days} days)")
        return cert

    async def renew_certificate(self, cert_id: str, validity_days: int = 90) -> Certificate:
        """Renew an existing certificate."""
        cert = self._certificates.get(cert_id)
        if not cert:
            raise ValueError(f"Certificate {cert_id} not found")

        now = datetime.now(timezone.utc)
        cert.status = CertificateStatus.VALID
        cert.issued_at = now
        cert.expires_at = now + timedelta(days=validity_days)
        cert.serial_number = uuid.uuid4().hex[:16].upper()
        cert.fingerprint = hashlib.sha256(f"{cert.common_name}{cert.serial_number}{now.isoformat()}".encode()).hexdigest()
        cert.pem_certificate = f"-----BEGIN CERTIFICATE-----\n{cert.fingerprint[:64]}\n-----END CERTIFICATE-----"
        logger.info(f"Certificate for '{cert.common_name}' renewed (valid until {cert.expires_at.date()})")
        return cert

    async def revoke_certificate(self, cert_id: str, reason: str = "unspecified") -> Certificate:
        cert = self._certificates.get(cert_id)
        if not cert:
            raise ValueError(f"Certificate {cert_id} not found")
        cert.status = CertificateStatus.REVOKED
        cert.pem_certificate = ""
        cert.pem_private_key = ""
        logger.warning(f"Certificate {cert_id} REVOKED: {reason}")
        return cert

    async def check_and_renew_expiring(self, days_threshold: int = 30) -> List[Certificate]:
        """Auto-renew certificates expiring within threshold."""
        renewed = []
        for cert in self._certificates.values():
            if cert.auto_renew and cert.renewal_due and cert.status == CertificateStatus.VALID:
                cert.status = CertificateStatus.PENDING_RENEWAL
                renewed_cert = await self.renew_certificate(cert.id)
                renewed.append(renewed_cert)
        if renewed:
            logger.info(f"Auto-renewed {len(renewed)} certificates")
        return renewed

    async def get_certificate(self, cert_id: str) -> Optional[Certificate]:
        return self._certificates.get(cert_id)

    async def list_certificates(
        self,
        tenant_id: Optional[str] = None,
        cluster_id: Optional[str] = None,
        status: Optional[CertificateStatus] = None,
        renewal_due_only: bool = False,
    ) -> List[Certificate]:
        certs = list(self._certificates.values())
        if tenant_id:
            certs = [c for c in certs if c.tenant_id == tenant_id]
        if cluster_id:
            certs = [c for c in certs if c.cluster_id == cluster_id]
        if status:
            certs = [c for c in certs if c.status == status]
        if renewal_due_only:
            certs = [c for c in certs if c.renewal_due]
        return certs

    def get_certificate_summary(self) -> Dict[str, Any]:
        certs = list(self._certificates.values())
        return {
            "total_certificates": len(certs),
            "by_status": {s.value: sum(1 for c in certs if c.status == s) for s in CertificateStatus},
            "renewal_due": sum(1 for c in certs if c.renewal_due),
            "auto_renew_enabled": sum(1 for c in certs if c.auto_renew),
        }
