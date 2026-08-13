"""Credential providers for certificate-backed PDF signing.

Providers resolve a PKCS#12 path and passphrase at signing time. They must not
log or expose the passphrase in representations or error messages.
"""

from __future__ import annotations

import platform
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class CredentialProviderError(RuntimeError):
    """Raised when signing credentials cannot be resolved safely."""


@dataclass(frozen=True)
class Pkcs12Credential:
    """Resolved PKCS#12 location and secret, held only for the signing call."""

    pfx_path: Path
    passphrase: str | bytes | None

    def __repr__(self) -> str:
        return f"Pkcs12Credential(pfx_path={self.pfx_path!r}, passphrase=<redacted>)"


class Pkcs12CredentialProvider(Protocol):
    """Resolve certificate material without changing the signing pipeline."""

    def resolve(self) -> Pkcs12Credential:
        ...


@dataclass(frozen=True)
class StaticPkcs12CredentialProvider:
    """Compatibility provider for an explicitly supplied PKCS#12 secret."""

    pfx_path: Path
    passphrase: str | bytes | None

    def resolve(self) -> Pkcs12Credential:
        return Pkcs12Credential(self.pfx_path, self.passphrase)


@dataclass(frozen=True)
class MacOSKeychainPkcs12CredentialProvider:
    """Resolve a PKCS#12 passphrase from a macOS generic-password item."""

    pfx_path: Path
    service: str
    account: str
    timeout_seconds: float = 10.0

    def resolve(self) -> Pkcs12Credential:
        if platform.system() != "Darwin":
            raise CredentialProviderError("macos_keychain_unavailable: platform is not macOS")
        if not self.service.strip() or not self.account.strip():
            raise CredentialProviderError("macos_keychain_invalid_locator")

        command = [
            "/usr/bin/security",
            "find-generic-password",
            "-s",
            self.service,
            "-a",
            self.account,
            "-w",
        ]
        try:
            completed = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
        except FileNotFoundError as exc:
            raise CredentialProviderError("macos_keychain_unavailable: security tool not found") from exc
        except subprocess.TimeoutExpired as exc:
            raise CredentialProviderError("macos_keychain_timeout") from exc
        except subprocess.CalledProcessError as exc:
            raise CredentialProviderError("macos_keychain_lookup_failed") from exc

        passphrase = completed.stdout.rstrip("\r\n")
        if not passphrase:
            raise CredentialProviderError("macos_keychain_empty_secret")
        return Pkcs12Credential(self.pfx_path, passphrase)
