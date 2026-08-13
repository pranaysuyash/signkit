from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from desktop_app.pdf import credentials
from desktop_app.pdf.digital_signer import DigitalSigningError, sign_pdf_with_certificate


def test_static_credential_repr_redacts_passphrase(tmp_path: Path) -> None:
    provider = credentials.StaticPkcs12CredentialProvider(tmp_path / "signer.p12", "secret-value")

    resolved = provider.resolve()

    assert resolved.pfx_path.name == "signer.p12"
    assert resolved.passphrase == "secret-value"
    assert "secret-value" not in repr(resolved)


def test_macos_keychain_provider_uses_fixed_argument_list_and_redacts_failures(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    calls: list[tuple[list[str], dict[str, object]]] = []

    class Completed:
        stdout = "secret-from-keychain\n"

    def fake_run(command: list[str], **kwargs: object) -> Completed:
        calls.append((command, kwargs))
        return Completed()

    monkeypatch.setattr(credentials.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(credentials.subprocess, "run", fake_run)
    provider = credentials.MacOSKeychainPkcs12CredentialProvider(
        tmp_path / "signer.p12",
        service="com.signkit.signer",
        account="operator@example.com",
    )

    resolved = provider.resolve()

    assert resolved.passphrase == "secret-from-keychain"
    assert calls[0][0] == [
        "/usr/bin/security",
        "find-generic-password",
        "-s",
        "com.signkit.signer",
        "-a",
        "operator@example.com",
        "-w",
    ]
    assert calls[0][1]["capture_output"] is True
    assert "secret-from-keychain" not in repr(provider)


def test_macos_keychain_provider_does_not_leak_subprocess_error(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(credentials.platform, "system", lambda: "Darwin")

    def fake_run(*_args: object, **_kwargs: object) -> object:
        raise subprocess.CalledProcessError(1, ["security"], stderr="secret-value")

    monkeypatch.setattr(credentials.subprocess, "run", fake_run)
    provider = credentials.MacOSKeychainPkcs12CredentialProvider(
        tmp_path / "signer.p12",
        service="com.signkit.signer",
        account="operator@example.com",
    )

    with pytest.raises(credentials.CredentialProviderError) as error:
        provider.resolve()

    assert "secret-value" not in str(error.value)


def test_signer_requires_exactly_one_credential_source(tmp_path: Path) -> None:
    provider = credentials.StaticPkcs12CredentialProvider(tmp_path / "signer.p12", "secret-value")

    with pytest.raises(DigitalSigningError, match="exactly_one_credential_source_required"):
        sign_pdf_with_certificate(str(tmp_path / "input.pdf"), str(tmp_path / "output.pdf"))

    with pytest.raises(DigitalSigningError, match="exactly_one_credential_source_required"):
        sign_pdf_with_certificate(
            str(tmp_path / "input.pdf"),
            str(tmp_path / "output.pdf"),
            str(tmp_path / "signer.p12"),
            credential_provider=provider,
        )
