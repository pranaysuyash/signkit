# F-006: Digital Certificate Support (PAdES) - Deep Research

**Feature ID:** F-006  
**Category:** Security & Compliance  
**Priority:** CRITICAL  
**Complexity:** High  
**Status:** Local PAdES baseline implemented; production trust and legal-operational integration remain open  
**Estimated Effort:** 4-6 weeks  
**Document Created:** April 10, 2026  

## Addendum (2026-08-12)

The first implementation stage is now complete locally. `desktop_app/pdf/digital_signer.py` loads a PKCS#12 certificate, creates a PAdES baseline detached PDF signature with `pyHanko`, verifies cryptographic validity and signed-revision integrity, records the certificate fingerprint and trust scope, promotes the output atomically, and writes a cryptographic artifact receipt. The explicit entry points are exposed through `desktop_app/pdf/signer.py` and `desktop_app/workflows/engine.py`.

This does not close the production boundary. B-12 remains responsible for unified UI/export integration, key custody, public or enterprise trust-chain policy, revocation and timestamp/LTV requirements, retention/recovery, legal claim review, and Tier 3 production-like evidence. The older phase checklist below is preserved as historical planning; the current implementation and acceptance state are tracked in `docs/expansion/SIGNKIT_CONTRACTDESK_WEB_EXPANSION_AGENT_TRACKER_2026-08-12.md` and `docs/expansion/SIGNKIT_CONTRACTDESK_WEB_SIGNED_ARTIFACT_CONTRACT_2026-08-12.md`.

The hardening pass also verifies that configured trust roots are enforced before output promotion. Current research confirms that pyHanko validates cryptographic integrity, certificate-chain trust, and incremental updates, but does not by itself establish every structural PAdES profile requirement. Timestamped and long-term profiles therefore require explicit RFC 3161, revocation, and retention decisions rather than being implied by a baseline signature.

The credential boundary now includes a macOS Keychain adapter. Apple documents Keychain Services as encrypted storage for passwords, keys, and certificates; the adapter uses the system `security` tool with a fixed argument list and redacted failure handling. This is a safer passphrase retrieval boundary, not proof of hardware-backed private-key custody. That production decision remains B-14.

Reference: [Apple Keychain Services](https://developer.apple.com/documentation/security/keychain-services)

---

## Executive Summary

Digital Certificate Support enables legally binding electronic signatures using PAdES (PDF Advanced Electronic Signatures) standard. This transforms SignKit from a convenience tool into an enterprise-grade solution compliant with eIDAS (EU), ESIGN Act (US), and UETA regulations.

### Key Benefits
- **Legal validity** - Signatures hold up in court
- **Non-repudiation** - Signer cannot deny signing
- **Document integrity** - Tampering is detectable
- **Enterprise adoption** - Required for B2B sales

### Business Value
- **Opens enterprise market** ($1000s/month vs $29)
- **Competitive differentiation** - Few desktop apps support this
- **Premium tier justification** - Certificate features = premium pricing
- **Compliance sales** - GDPR, HIPAA, SOX requirements

---

## Market Research

### Regulatory Landscape

#### European Union (eIDAS)
- **Simple Electronic Signature** - Basic (image-based)
- **Advanced Electronic Signature (AdES)** - ✓ Our target
- **Qualified Electronic Signature (QES)** - Hardware token required

#### United States
- **ESIGN Act (2000)** - Electronic signatures legally binding
- **UETA** - State-level uniformity
- **21 CFR Part 11** - FDA compliance for pharma

#### Other Regions
- **PIPEDA** (Canada)
- **ETSI EN 319 122** (Technical standard)
- **ISO 32000-2** (PDF 2.0 standard)

### Competitor Analysis

| Product | Certificate Support | Price | Notes |
|---------|---------------------|-------|-------|
| **Adobe Acrobat** | Full PAdES | $239/year | Industry standard |
| **DocuSign** | QES via partners | $25+/mo | Cloud-based |
| **SignNow** | PAdES-LTA | $20+/mo | Limited formats |
| **PDFelement** | Basic | $79/year | Limited compliance |
| **Preview (macOS)** | None | Free | No certificate support |
| **SignKit** | **None** | $29 | **GAP TO FILL** |

### Market Opportunity

**Target Segments:**
1. **Law firms** - Require legally binding signatures
2. **Healthcare** - HIPAA compliance needs
3. **Financial services** - Audit trail requirements
4. **Government** - eIDAS compliance (EU)
5. **Pharma** - 21 CFR Part 11 compliance

**User Quotes:**
- *"I can't use SignKit for contracts without legal validity"*
- *"My clients require certificate-based signatures"*
- *"Compliance team won't approve basic image signatures"*

---

## Technical Specification

### PAdES Standards

```
PAdES (PDF Advanced Electronic Signatures)
├── PAdES-B (Basic)
│   └── RSA signature + certificate
├── PAdES-T (Timestamp)
│   └── + RFC 3161 timestamp
├── PAdES-LT (Long Term)
│   └── + revocation info
└── PAdES-LTA (Long Term with Archive)
    └── + document timestamp
```

**Implementation Target:** PAdES-B to PAdES-T (sufficient for most use cases)

### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│               Digital Signature System                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Certificate Management                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Load Cert    │  │ Validate     │  │ Store Secure │       │
│  │ (PKCS#12)    │  │ Chain        │  │ (Keychain)   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
│  Signing Process                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Create       │  │ Sign Digest  │  │ Embed in PDF │       │
│  │ Digest       │──▶│ (Private Key)│──▶│ (PAdES)      │       │
│  │ (SHA-256)    │  │              │  │              │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
│  Verification                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Extract      │  │ Verify Cert  │  │ Check        │       │
│  │ Signature    │──▶│ Chain        │──▶│ Document     │       │
│  │              │  │              │  │ Integrity    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. Certificate Handler
```python
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import hashlib

class CertificateManager:
    """Manages digital certificates for signing."""
    
    SUPPORTED_FORMATS = {'.p12', '.pfx', '.pem', '.crt'}
    
    def __init__(self):
        self.certificates: Dict[str, Certificate] = {}
        self.storage = SecureCertificateStorage()
    
    def load_certificate(
        self,
        path: str,
        password: Optional[str] = None
    ) -> Certificate:
        """Load certificate from PKCS#12 or PEM file."""
        
        if path.endswith(('.p12', '.pfx')):
            return self._load_pkcs12(path, password)
        elif path.endswith('.pem'):
            return self._load_pem(path)
        else:
            raise ValueError(f"Unsupported format: {path}")
    
    def _load_pkcs12(self, path: str, password: Optional[str]) -> Certificate:
        """Load PKCS#12 container (contains cert + private key)."""
        from cryptography.hazmat.primitives.serialization import pkcs12
        
        with open(path, 'rb') as f:
            p12_data = f.read()
        
        private_key, certificate, additional_certs = pkcs12.load_key_and_certificates(
            p12_data,
            password.encode() if password else None
        )
        
        return Certificate(
            private_key=private_key,
            certificate=certificate,
            ca_chain=additional_certs or [],
            source=path
        )
    
    def validate_certificate(self, cert: Certificate) -> ValidationResult:
        """Validate certificate chain and expiry."""
        
        # Check expiry
        now = datetime.utcnow()
        if cert.certificate.not_valid_before > now:
            return ValidationResult(False, "Certificate not yet valid")
        
        if cert.certificate.not_valid_after < now:
            return ValidationResult(False, "Certificate expired")
        
        # Check purpose
        if not self._has_signing_usage(cert.certificate):
            return ValidationResult(False, "Certificate not valid for signing")
        
        # Validate chain
        try:
            self._validate_chain(cert)
            return ValidationResult(True, "Valid")
        except Exception as e:
            return ValidationResult(False, f"Chain validation failed: {e}")
    
    def _has_signing_usage(self, cert: x509.Certificate) -> bool:
        """Check if certificate is valid for digital signatures."""
        try:
            key_usage = cert.extensions.get_extension_for_oid(
                x509.oid.ExtensionOID.KEY_USAGE
            )
            return key_usage.value.digital_signature
        except x509.ExtensionNotFound:
            # If no KeyUsage extension, assume valid
            return True
```

#### 2. PDF Signer
```python
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import signers, fields
from pyhanko_certvalidator import ValidationContext

class PdfDigitalSigner:
    """Signs PDFs with digital certificates (PAdES)."""
    
    def __init__(self, certificate: Certificate):
        self.cert = certificate
        self.signer = self._create_signer()
    
    def _create_signer(self) -> signers.SimpleSigner:
        """Create signer from certificate."""
        return signers.SimpleSigner(
            signing_cert=self.cert.certificate,
            signing_key=self.cert.private_key,
            cert_registry=signers.SimpleCertStore(
                certs=self.cert.ca_chain
            )
        )
    
    def sign_pdf(
        self,
        input_path: str,
        output_path: str,
        signature_appearance: Optional[SignatureAppearance] = None,
        timestamp_url: Optional[str] = None
    ) -> SigningResult:
        """Sign PDF with digital certificate."""
        
        # Load PDF
        with open(input_path, 'rb') as f:
            pdf_writer = IncrementalPdfFileWriter(f)
        
        # Create signature field if not exists
        fields.append_signature_field(
            pdf_writer,
            sig_field_spec=fields.SigFieldSpec(
                sig_field_name='Signature1',
                on_page=0,
                box=(100, 100, 300, 200)  # x1, y1, x2, y2
            )
        )
        
        # Prepare signature metadata
        signature_meta = signers.PdfSignatureMetadata(
            field_name='Signature1',
            subfilter=signers.PdfSignedDataSubFilter.ADOBE_PKCS7_DETACHED,
            certify=False,
            reason='Document signed digitally',
            location='SignKit',
            contact_info='support@signkit.work'
        )
        
        # Add timestamp if URL provided
        if timestamp_url:
            timestamper = signers.PdfTimeStamper(timestamp_url)
            signature_meta = signature_meta._replace(
                embed_validation_info=True
            )
        
        # Sign the PDF
        with open(output_path, 'wb') as out:
            signers.PdfSigner(
                signature_meta,
                self.signer
            ).sign_pdf(
                pdf_writer,
                output=out,
                appearance=signature_appearance
            )
        
        return SigningResult(
            output_path=output_path,
            signature_valid=True,
            timestamp=datetime.utcnow()
        )
```

#### 3. Signature Appearance
```python
class SignatureAppearance:
    """Visual appearance of digital signature on PDF."""
    
    def __init__(
        self,
        include_name: bool = True,
        include_date: bool = True,
        include_logo: bool = True,
        background_color: Tuple[int, int, int] = (255, 255, 255),
        border_color: Tuple[int, int, int] = (0, 0, 255),
        custom_text: Optional[str] = None
    ):
        self.include_name = include_name
        self.include_date = include_date
        self.include_logo = include_logo
        self.background_color = background_color
        self.border_color = border_color
        self.custom_text = custom_text
    
    def generate_appearance_stream(
        self,
        certificate: Certificate,
        width: float,
        height: float
    ) -> bytes:
        """Generate PDF appearance stream."""
        # Create visual representation showing:
        # - Signer name from certificate
        # - Date/time of signing
        # - SignKit logo
        # - "Digitally signed by" text
        # - Green checkmark for valid
        pass
```

#### 4. Verification
```python
class SignatureVerifier:
    """Verifies digital signatures in PDFs."""
    
    def verify_signature(self, pdf_path: str) -> VerificationReport:
        """Verify all signatures in PDF."""
        
        from pyhanko.sign.validation import validate_pdf_signature
        
        report = VerificationReport(pdf_path)
        
        with open(pdf_path, 'rb') as f:
            pdf_reader = PdfFileReader(f)
            
            for sig_field in self._get_signature_fields(pdf_reader):
                try:
                    result = validate_pdf_signature(
                        pdf_reader,
                        sig_field.name,
                        validation_context=self._create_validation_context()
                    )
                    
                    report.add_signature(
                        SignatureInfo(
                            field_name=sig_field.name,
                            valid=result.valid,
                            signer=result.signer_cert.subject,
                            signing_time=result.signing_time,
                            integrity_intact=result.intact,
                            trusted=result.trusted
                        )
                    )
                    
                except Exception as e:
                    report.add_error(sig_field.name, str(e))
        
        return report
```

### Dependencies

```txt
# Cryptography
cryptography>=41.0.0
pyhanko>=0.21.0
pyhanko-certvalidator>=0.24.0

# Certificate handling
asn1crypto>=1.5.0
oscrypto>=1.3.0

# Optional: Hardware token support
PyKCS11>=1.5.10  # For smart cards
```

---

## User Stories

### Story 1: Legal Contract
**As a** lawyer  
**I want to** sign contracts with legally binding signatures  
**So that** they hold up in court  

**Acceptance Criteria:**
- Can load my bar association certificate
- Signature shows as "Digitally Signed by [Name]"
- Validates in Adobe Reader
- Meets eIDAS requirements

### Story 2: Certificate Management
**As a** business user  
**I want to** securely store my signing certificate  
**So that** I don't have to re-enter password each time  

**Acceptance Criteria:**
- Secure storage in OS keychain
- Password required only on first use
- Can revoke/change certificate
- Clear which certificate is active

### Story 3: Signature Verification
**As a** recipient  
**I want to** verify a signed PDF  
**So that** I know it's authentic and untampered  

**Acceptance Criteria:**
- Shows signer identity
- Shows signing timestamp
- Indicates if document modified since signing
- Clear valid/invalid status

---

## Implementation Plan

### Phase 1: Foundation (Week 1-2)
- [ ] Research PAdES implementation details
- [ ] Set up cryptography dependencies
- [ ] Implement certificate loading (PKCS#12)
- [ ] Certificate validation logic
- [ ] Secure storage integration

**Deliverable:** Can load and validate certificates

### Phase 2: Basic Signing (Week 2-3)
- [ ] Implement PAdES-B signing
- [ ] Create signature field in PDF
- [ ] Generate signature appearance
- [ ] Test with various certificates
- [ ] Error handling

**Deliverable:** Can sign PDFs with certificates

### Phase 3: Advanced Features (Week 3-4)
- [ ] PAdES-T (timestamp) support
- [ ] Multiple signature support
- [ ] Signature appearance customization
- [ ] Certificate chain validation
- [ ] OCSP/CRL checking

**Deliverable:** Production-grade signing

### Phase 4: Verification (Week 4-5)
- [ ] Signature verification logic
- [ ] Visual verification report
- [ ] Tampering detection
- [ ] Validation details display

**Deliverable:** Can verify signed PDFs

### Phase 5: UI/UX (Week 5-6)
- [ ] Certificate management dialog
- [ ] Sign with certificate option
- [ ] Verification dialog
- [ ] Security indicators
- [ ] Help documentation

**Deliverable:** User-friendly interface

---

## Testing Strategy

### Certificate Types to Test
1. **Self-signed** - Basic testing
2. **Let's Encrypt** - Free certificates
3. **Commercial CA** - DigiCert, Sectigo
4. **Enterprise CA** - Internal certificates
5. **Expired certificates** - Error handling
6. **Revoked certificates** - CRL testing

### Test Scenarios
- Sign with different algorithms (RSA, ECDSA)
- Large PDFs (100+ MB)
- Multi-page documents
- Already signed documents (countersign)
- Corrupted certificates
- Wrong password

---

## Success Metrics

### Adoption
- **Target:** 30% of business users adopt
- **Measurement:** Certificate usage tracking
- **Success:** >25% adoption

### Validation
- **Target:** 100% successful validation in Adobe Reader
- **Measurement:** Cross-platform testing
- **Success:** Validates in all major readers

### Compliance
- **Target:** Pass eIDAS validation tools
- **Measurement:** Third-party compliance testing
- **Success:** Certified compliant

---

## Business Model Impact

### New Tier Structure
- **Basic ($29):** Image signatures only
- **Professional ($79):** Digital signatures + 1 certificate
- **Enterprise ($199):** Unlimited + team management

### Revenue Impact
- Certificate feature drives upgrades
- Enterprise tier opens new market
- Estimated +60% revenue increase

---

## Security Considerations

### Certificate Storage
- Use OS keychain (macOS Keychain, Windows Certificate Store)
- Memory-only private keys (never persist unencrypted)
- Automatic locking after timeout

### Audit Trail
- Log all signing operations
- Include certificate thumbprint
- Timestamp with UTC
- Tamper-evident logs

### Compliance
- GDPR Article 25 (data protection by design)
- eIDAS Regulation (EU) 910/2014
- SOX compliance for financial data

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Complex cryptography** | High | Use established libraries (pyhanko) |
| **Certificate expiration** | Medium | Clear warnings, auto-renewal prompts |
| **User confusion** | Medium | Simple UI, clear documentation |
| **Legal liability** | High | Disclaimer, terms of service |
| **Performance issues** | Low | Optimize crypto operations |

---

## References

- [ETSI EN 319 142-1](https://www.etsi.org/deliver/etsi_en/319100_319199/31914201/) - PAdES Standard
- [eIDAS Regulation](https://eur-lex.europa.eu/eli/reg/2014/910) - EU Electronic signatures
- [pyhanko Documentation](https://pyhanko.readthedocs.io/) - Python PDF signing
- [Adobe Digital Signatures Guide](https://helpx.adobe.com/acrobat/using/digital-signatures.html)

---

**Document Status:** Complete  
**Next Review:** May 10, 2026
