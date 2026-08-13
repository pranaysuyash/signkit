from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID

from desktop_app.pdf.digital_signer import DigitalSigningError, sign_pdf_with_certificate


def _write_pkcs12(tmp_path: Path, stem: str, common_name: str) -> tuple[Path, Path]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])
    now = datetime.now(timezone.utc)
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=30))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(key, hashes.SHA256())
    )
    passphrase = b"trust-test-passphrase"
    pfx_path = tmp_path / f"{stem}.p12"
    pfx_path.write_bytes(
        pkcs12.serialize_key_and_certificates(
            name=b"signer",
            key=key,
            cert=certificate,
            cas=None,
            encryption_algorithm=serialization.BestAvailableEncryption(passphrase),
        )
    )
    cert_path = tmp_path / f"{stem}.pem"
    cert_path.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
    return pfx_path, cert_path


def test_signing_rejects_untrusted_certificate_before_promoting_output(tmp_path: Path) -> None:
    fixture = Path(__file__).resolve().parent / "fixtures" / "sample.pdf"
    signer_pfx, _ = _write_pkcs12(tmp_path, "signer", "SignKit signer")
    _, wrong_root = _write_pkcs12(tmp_path, "wrong-root", "Wrong trust root")
    output_path = tmp_path / "untrusted.pdf"
    receipt_path = tmp_path / "untrusted.pdf.receipt.json"

    with pytest.raises(DigitalSigningError, match="verification_failed"):
        sign_pdf_with_certificate(
            fixture,
            output_path,
            signer_pfx,
            passphrase="trust-test-passphrase",
            trust_root_paths=[wrong_root],
            receipt_path=receipt_path,
        )

    assert not output_path.exists()
    assert not receipt_path.exists()


def test_signing_rejects_unauthorized_operator_before_promoting_output(tmp_path: Path) -> None:
    fixture = Path(__file__).resolve().parent / "fixtures" / "sample.pdf"
    signer_pfx, _ = _write_pkcs12(tmp_path, "authorized-test", "SignKit signer")
    output_path = tmp_path / "unauthorized.pdf"

    with pytest.raises(DigitalSigningError, match="signer_authorization_failed"):
        sign_pdf_with_certificate(
            fixture,
            output_path,
            signer_pfx,
            passphrase="trust-test-passphrase",
            operator_subject="operator-a",
            authorized_subjects=["operator-b"],
        )

    assert not output_path.exists()


def test_signing_rejects_ambiguous_or_invalid_timestamp_configuration(tmp_path: Path) -> None:
    fixture = Path(__file__).resolve().parent / "fixtures" / "sample.pdf"
    signer_pfx, _ = _write_pkcs12(tmp_path, "timestamp-test", "SignKit signer")

    with pytest.raises(DigitalSigningError, match="exactly_one_timestamp_source_required"):
        sign_pdf_with_certificate(
            fixture,
            tmp_path / "ambiguous.pdf",
            signer_pfx,
            passphrase="trust-test-passphrase",
            timestamp_url="https://tsa.example.test",
            timestamper=object(),
        )

    with pytest.raises(DigitalSigningError, match="invalid_timestamp_url"):
        sign_pdf_with_certificate(
            fixture,
            tmp_path / "invalid.pdf",
            signer_pfx,
            passphrase="trust-test-passphrase",
            timestamp_url="file:///tmp/timestamp",
        )
