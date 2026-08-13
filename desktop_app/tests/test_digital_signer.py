from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID

from desktop_app.pdf.digital_signer import (
    DigitalSigningError,
    sign_pdf_with_certificate,
    verify_pdf_signature,
)


SAMPLE_PDF = Path(__file__).parent / "fixtures" / "sample.pdf"


def _make_test_certificate(path: Path, passphrase: bytes | None = None) -> None:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name(
        [x509.NameAttribute(NameOID.COMMON_NAME, "SignKit Test Signer")]
    )
    now = datetime.now(timezone.utc)
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=1))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=True,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .sign(key, hashes.SHA256())
    )
    encryption = (
        serialization.BestAvailableEncryption(passphrase)
        if passphrase
        else serialization.NoEncryption()
    )
    path.write_bytes(
        pkcs12.serialize_key_and_certificates(
            b"signkit-test",
            key,
            certificate,
            None,
            encryption,
        )
    )


def test_sign_and_verify_pades_pdf_with_pkcs12_certificate(tmp_path: Path) -> None:
    pfx = tmp_path / "signer.p12"
    output = tmp_path / "signed.pdf"
    _make_test_certificate(pfx)

    result = sign_pdf_with_certificate(
        str(SAMPLE_PDF),
        str(output),
        str(pfx),
        operator_subject="operator@example.test",
        execution_id="execution-1",
    )

    assert result.verification.valid is True
    assert result.verification.intact is True
    assert result.verification.trusted is True
    assert result.verification.coverage == "ENTIRE_FILE"
    assert result.verification.modification_level == "NONE"
    assert result.receipt.cryptographic_signature is True
    assert result.receipt.signature_semantics == "pades_baseline_b_detached"
    assert Path(result.receipt_path).exists()


def test_tampered_signed_revision_is_reported_as_not_intact(tmp_path: Path) -> None:
    pfx = tmp_path / "signer.p12"
    output = tmp_path / "signed.pdf"
    _make_test_certificate(pfx)
    sign_pdf_with_certificate(str(SAMPLE_PDF), str(output), str(pfx))

    tampered = tmp_path / "tampered.pdf"
    payload = bytearray(output.read_bytes())
    signed_revision_end = payload.find(b"%%EOF")
    assert signed_revision_end > 0
    payload[signed_revision_end - 10] = (payload[signed_revision_end - 10] + 1) % 255
    tampered.write_bytes(payload)

    verification = verify_pdf_signature(str(tampered))

    assert verification.intact is False
    assert not (verification.valid and verification.intact and verification.trusted)


def test_wrong_pkcs12_passphrase_fails_without_output(tmp_path: Path) -> None:
    pfx = tmp_path / "signer.p12"
    output = tmp_path / "signed.pdf"
    _make_test_certificate(pfx, passphrase=b"correct")

    with pytest.raises(DigitalSigningError):
        sign_pdf_with_certificate(
            str(SAMPLE_PDF),
            str(output),
            str(pfx),
            passphrase="wrong",
        )
    assert not output.exists()
