"""Certificate-backed PDF signing and verification using pyHanko.

This module is intentionally separate from image placement. Image placement
creates a visible mark; this module creates and verifies a certificate-backed
PDF signature using the PAdES detached signature subfilter.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from desktop_app.pdf.credentials import Pkcs12CredentialProvider
from desktop_app.workflows.verifier import (
    ArtifactReceipt,
    build_artifact_receipt,
    write_artifact_receipt,
)

try:
    from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
    from pyhanko.pdf_utils.reader import PdfFileReader
    from pyhanko.sign import fields, signers
    from pyhanko.sign.signers import SimpleSigner
    from pyhanko.sign.timestamps import HTTPTimeStamper
    from pyhanko.sign.validation import validate_pdf_signature
    from pyhanko_certvalidator import ValidationContext
except ImportError as exc:  # pragma: no cover - exercised in dependency guidance
    IncrementalPdfFileWriter = None  # type: ignore[assignment]
    PdfFileReader = None  # type: ignore[assignment]
    fields = None  # type: ignore[assignment]
    signers = None  # type: ignore[assignment]
    SimpleSigner = None  # type: ignore[assignment]
    HTTPTimeStamper = None  # type: ignore[assignment]
    validate_pdf_signature = None  # type: ignore[assignment]
    ValidationContext = None  # type: ignore[assignment]
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


class DigitalSigningError(RuntimeError):
    """Raised when certificate-backed signing or verification cannot complete."""


@dataclass(frozen=True)
class DigitalSignatureVerification:
    valid: bool
    intact: bool
    trusted: bool
    signer_subject: str
    certificate_fingerprint: str
    coverage: str
    modification_level: str
    signature_count: int


@dataclass(frozen=True)
class DigitalSignatureResult:
    output_path: str
    receipt_path: str
    verification: DigitalSignatureVerification
    receipt: ArtifactReceipt

    def to_dict(self) -> dict[str, object]:
        return {
            "output_path": self.output_path,
            "receipt_path": self.receipt_path,
            "verification": asdict(self.verification),
            "receipt": self.receipt.to_dict(),
        }


def _require_dependency() -> None:
    if _IMPORT_ERROR is not None:
        raise DigitalSigningError(
            "Certificate-backed PDF signing requires the optional pyHanko dependencies. "
            "Install desktop_app/requirements-pdf-optional.txt."
        ) from _IMPORT_ERROR


def _passphrase_bytes(passphrase: str | bytes | None) -> bytes | None:
    if passphrase is None or isinstance(passphrase, bytes):
        return passphrase
    return passphrase.encode("utf-8")


def _certificate_fingerprint(certificate: object) -> str:
    return hashlib.sha256(certificate.dump()).hexdigest()  # type: ignore[union-attr]


def _subject_label(certificate: object) -> str:
    native = certificate.subject.native  # type: ignore[union-attr]
    if isinstance(native, dict):
        for key in ("common_name", "organization_name", "organizational_unit_name"):
            value = native.get(key)
            if value:
                return str(value)
    return str(native)


def load_certificate_signer(
    pfx_path: str,
    passphrase: str | bytes | None = None,
) -> SimpleSigner:
    """Load a PKCS#12 signer without logging or persisting its private key."""

    _require_dependency()
    path = Path(pfx_path)
    if not path.is_file():
        raise DigitalSigningError(f"Certificate bundle not found: {path}")
    try:
        return SimpleSigner.load_pkcs12(
            pfx_file=str(path),
            passphrase=_passphrase_bytes(passphrase),
        )
    except Exception as exc:
        raise DigitalSigningError(f"Could not load certificate bundle: {exc}") from exc


def _load_trust_roots(paths: Iterable[str]) -> list[object]:
    _require_dependency()
    from pyhanko.keys import load_cert_from_pemder

    roots = []
    for path in paths:
        cert_path = Path(path)
        if not cert_path.is_file():
            raise DigitalSigningError(f"Trust certificate not found: {cert_path}")
        roots.append(load_cert_from_pemder(str(cert_path)))
    return roots


def verify_pdf_signature(
    pdf_path: str,
    *,
    trust_root_paths: Iterable[str] = (),
) -> DigitalSignatureVerification:
    """Validate the newest embedded PDF signature against configured trust roots.

    When no trust roots are supplied, the embedded signer certificate is used
    as the explicit trust root. This proves cryptographic integrity and trust
    in the configured signer certificate, not public-CA or legal qualification.
    """

    _require_dependency()
    path = Path(pdf_path)
    if not path.is_file():
        raise DigitalSigningError(f"Signed PDF not found: {path}")
    try:
        with path.open("rb") as handle:
            reader = PdfFileReader(handle)
            signatures = reader.embedded_signatures
            if not signatures:
                raise DigitalSigningError("PDF contains no embedded digital signatures")
            embedded = signatures[-1]
            roots = _load_trust_roots(trust_root_paths)
            if not roots:
                roots = [embedded.signer_cert]
            status = validate_pdf_signature(
                embedded,
                signer_validation_context=ValidationContext(trust_roots=roots),
            )
            coverage = getattr(status.coverage, "name", str(status.coverage))
            modification_level = getattr(
                status.modification_level,
                "name",
                str(status.modification_level),
            )
            return DigitalSignatureVerification(
                valid=bool(status.valid),
                intact=bool(status.intact),
                trusted=bool(status.trusted),
                signer_subject=_subject_label(embedded.signer_cert),
                certificate_fingerprint=_certificate_fingerprint(embedded.signer_cert),
                coverage=coverage,
                modification_level=modification_level,
                signature_count=len(signatures),
            )
    except DigitalSigningError:
        raise
    except Exception as exc:
        raise DigitalSigningError(f"Could not validate PDF signature: {exc}") from exc


def sign_pdf_with_certificate(
    input_pdf_path: str,
    output_pdf_path: str,
    pfx_path: str | None = None,
    *,
    passphrase: str | bytes | None = None,
    credential_provider: Pkcs12CredentialProvider | None = None,
    field_name: str = "SignKitSignature",
    box: tuple[float, float, float, float] = (72, 72, 300, 150),
    reason: str = "Document signed with SignKit certificate",
    location: str = "SignKit local workspace",
    contact_info: str | None = None,
    operator_subject: str | None = None,
    authorized_subjects: Iterable[str] = (),
    execution_id: str | None = None,
    trust_root_paths: Iterable[str] = (),
    timestamp_url: str | None = None,
    timestamper: object | None = None,
    timestamp_timeout: float = 5.0,
    embed_validation_info: bool = False,
    receipt_path: str | None = None,
) -> DigitalSignatureResult:
    """Create a certificate-backed PAdES PDF and verify it before promotion."""

    _require_dependency()
    if (pfx_path is None) == (credential_provider is None):
        raise DigitalSigningError("exactly_one_credential_source_required")
    if credential_provider is not None:
        try:
            credential = credential_provider.resolve()
        except Exception as exc:
            raise DigitalSigningError(f"credential_provider_failed:{exc}") from exc
        pfx_path = str(credential.pfx_path)
        passphrase = credential.passphrase
    assert pfx_path is not None
    if timestamp_url and timestamper is not None:
        raise DigitalSigningError("exactly_one_timestamp_source_required")
    if timestamp_url:
        if HTTPTimeStamper is None:
            raise DigitalSigningError("timestamp_provider_unavailable")
        if not timestamp_url.startswith(("http://", "https://")):
            raise DigitalSigningError("invalid_timestamp_url")
        timestamper = HTTPTimeStamper(timestamp_url, timeout=timestamp_timeout)
    input_path = Path(input_pdf_path)
    output_path = Path(output_pdf_path)
    if not input_path.is_file():
        raise DigitalSigningError(f"Input PDF not found: {input_path}")
    if input_path.resolve() == output_path.resolve():
        raise DigitalSigningError("In-place cryptographic PDF signing is not allowed")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    trust_roots = tuple(trust_root_paths)
    certificate_signer = load_certificate_signer(pfx_path, passphrase)
    allowed_subjects = frozenset(subject for subject in authorized_subjects if subject)
    if allowed_subjects and (operator_subject is None or operator_subject not in allowed_subjects):
        raise DigitalSigningError("signer_authorization_failed")
    temporary = tempfile.NamedTemporaryFile(
        prefix=f".{output_path.name}.",
        suffix=".pdf",
        dir=output_path.parent,
        delete=False,
    )
    temporary_path = Path(temporary.name)
    temporary.close()
    try:
        metadata = signers.PdfSignatureMetadata(
            field_name=field_name,
            md_algorithm="sha256",
            subfilter=fields.SigSeedSubFilter.PADES,
            reason=reason,
                location=location,
                contact_info=contact_info,
                name=_subject_label(certificate_signer.signing_cert),
                embed_validation_info=embed_validation_info,
            )
        field_spec = fields.SigFieldSpec(
            sig_field_name=field_name,
            on_page=0,
            box=box,
        )
        with input_path.open("rb") as source, temporary_path.open("wb") as target:
            writer = IncrementalPdfFileWriter(source)
            signers.PdfSigner(
                metadata,
                certificate_signer,
                timestamper=timestamper,
                new_field_spec=field_spec,
            ).sign_pdf(writer, output=target)

            verification = verify_pdf_signature(
                str(temporary_path),
                trust_root_paths=trust_roots,
            )
            if not (verification.valid and verification.intact and verification.trusted):
                raise DigitalSigningError(
                    "verification_failed: "
                    f"valid={verification.valid} "
                    f"intact={verification.intact} "
                    f"trusted={verification.trusted}"
                )
        os.replace(temporary_path, output_path)
        final_receipt_path = Path(receipt_path or f"{output_path}.receipt.json")
        receipt = build_artifact_receipt(
            str(input_path),
            str(output_path),
            operator_subject=operator_subject,
            execution_id=execution_id,
            artifact_type="cryptographic_pdf_signature",
            signature_semantics="pades_baseline_b_detached",
            cryptographic_signature=True,
            certificate_fingerprint=verification.certificate_fingerprint,
            trust_scope=("configured_trust_roots" if trust_roots else "embedded_signer_certificate"),
        )
        write_artifact_receipt(receipt, str(final_receipt_path))
        return DigitalSignatureResult(
            output_path=str(output_path),
            receipt_path=str(final_receipt_path),
            verification=verification,
            receipt=receipt,
        )
    except DigitalSigningError:
        raise
    except Exception as exc:
        raise DigitalSigningError(f"Could not create cryptographic PDF signature: {exc}") from exc
    finally:
        if temporary_path.exists():
            temporary_path.unlink()
