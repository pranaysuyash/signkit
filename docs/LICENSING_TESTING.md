# Licensing System Testing Guide

> Current contract (2026-08-13): paid access requires a provider-issued,
> Ed25519-signed `EntitlementReceipt` and an explicitly configured public-key
> ring. The historical key-only and `pranay@example.com` instructions below
> are retained for repository history only. They do not describe current
> production behavior. See `docs/decisions/ADR-0151-signed-local-entitlement-
> activation.md` for the canonical boundary.

## Current local contract

Use a disposable test keyring and a signed fixture when exercising paid gates.
Do not put a provider API token or signing secret in the desktop environment.
The local test suite provides the canonical signing fixture and verifies:

- receipt signature and canonical-payload tamper detection;
- receipt-owned plan and add-on grants;
- unknown, revoked, expired, unsigned, and key-only fail-closed behavior;
- same-activation replay and different-entitlement conflict behavior;
- explicit `SIGNKIT_LICENSE_TEST_MODE=1` isolation for the historical test key.

The activation dialog expects signed receipt JSON. A raw provider key is not
purchase evidence until a provider adapter verifies it and produces the
normalized receipt. A real provider activation is still an open `QA-15` gate.

The remainder of this file is historical procedure retained for audit context.

## Overview

The Signature Extractor application implements a licensing system that restricts core functionality (export and PDF operations) when no valid license is present. This guide covers how to test both licensed and trial modes during development.

## License Storage Location

The license file is stored at:
```
~/.signature_extractor/license.json
```

**Full paths by operating system:**
- **macOS/Linux**: `~/.signature_extractor/license.json`
- **Windows**: `C:\Users\[username]\.signature_extractor\license.json`

## Testing Scenarios

### 1. Trial Mode Testing (No License)

**To activate trial mode:**
1. Delete the license file:
   ```bash
   rm ~/.signature_extractor/license.json
   ```
2. Or rename the directory temporarily:
   ```bash
   mv ~/.signature_extractor ~/.signature_extractor_backup
   ```

**Expected behavior in trial mode:**
- ❌ Export operations blocked (PNG, JPG export)
- ❌ PDF paste operations blocked
- ❌ PDF save operations blocked
- ✅ Image processing and preview works normally
- ✅ PDF viewing works normally
- ✅ Signature placement preview works
- 📋 License menu shows "⚠ No License (Trial Mode)"

### 2. Licensed Mode Testing (Test License)

**To activate test license:**
1. Open the application
2. Go to **License → Enter License Key...**
3. Enter: `pranay@example.com`
4. Click OK

**Expected behavior with test license:**
- ✅ All export operations enabled
- ✅ All PDF operations enabled
- ✅ Full functionality available
- 📋 License menu shows "✓ Licensed (pranay@example.com)"
- 🧪 Status indicates "Test License Active"

### 3. Regular License Testing

**To test with a regular license:**
1. Enter any license key with 6+ characters (e.g., "LICENSE-KEY-123")
2. Optionally provide an email address

**Expected behavior:**
- ✅ All functionality enabled (same as test license)
- 📋 Shows "✓ Licensed" with email if provided
- 🔒 No "test license" indicator

## License File Format

The license file (`license.json`) contains:
```json
{
  "key": "pranay@example.com",
  "email": "pranay@example.com", 
  "is_test_license": true,
  "validated_at": "2025-11-06T20:59:50.982157"
}
```

**Fields:**
- `key`: The license key entered by user
- `email`: Optional email address
- `is_test_license`: Boolean indicating if this is the test license
- `validated_at`: ISO timestamp of when license was saved

## Testing Commands

### Quick Status Check
```bash
python -c "
import sys; sys.path.insert(0, 'desktop_app')
from license import get_license_status_info
is_licensed, status, is_test = get_license_status_info()
print(f'Status: {status}')
print(f'Is Test License: {is_test}')
"
```

### Check Operation Permissions
```bash
python -c "
import sys; sys.path.insert(0, 'desktop_app')
from license import check_export_license, check_pdf_operations_license
print(f'Export allowed: {check_export_license()}')
print(f'PDF operations allowed: {check_pdf_operations_license()}')
"
```

### Reset to Trial Mode
```bash
rm ~/.signature_extractor/license.json
echo 'License removed - app is now in trial mode'
```

### Activate Test License
```bash
python -c "
import sys; sys.path.insert(0, 'desktop_app')
from license import save_license, TEST_LICENSE_EMAIL
save_license(TEST_LICENSE_EMAIL)
print(f'Test license activated: {TEST_LICENSE_EMAIL}')
"
```

## Development Testing Workflow

### Complete Test Cycle
1. **Start in trial mode** - Delete license file
2. **Test restrictions** - Try export/PDF operations (should be blocked)
3. **Activate test license** - Enter `pranay@example.com`
4. **Test full functionality** - Try export/PDF operations (should work)
5. **Test regular license** - Enter different license key
6. **Reset for next test** - Delete license file

### Automated Test Script
```bash
#!/bin/bash
# Complete licensing test script

echo "=== Licensing System Test ==="

# Remove existing license
rm -f ~/.signature_extractor/license.json
echo "1. Reset to trial mode ✓"

# Test trial mode
python -c "
import sys; sys.path.insert(0, 'desktop_app')
from license import check_export_license, get_license_status_info
_, status, _ = get_license_status_info()
export_allowed = check_export_license()
print(f'2. Trial mode: {status} - Export: {export_allowed} ✓')
"

# Test license activation
python -c "
import sys; sys.path.insert(0, 'desktop_app')
from license import save_license, check_export_license, get_license_status_info, TEST_LICENSE_EMAIL
save_license(TEST_LICENSE_EMAIL)
_, status, is_test = get_license_status_info()
export_allowed = check_export_license()
print(f'3. Test license: {status} - Export: {export_allowed} - Test: {is_test} ✓')
"

echo "=== Test Complete ==="
```

## Troubleshooting

### License Not Recognized
- Check file exists: `ls -la ~/.signature_extractor/`
- Check file contents: `cat ~/.signature_extractor/license.json`
- Verify JSON format is valid

### Permissions Issues
- Ensure directory is writable: `ls -ld ~/.signature_extractor/`
- Check file permissions: `ls -la ~/.signature_extractor/license.json`

### App Not Reflecting Changes
- Restart the application after manual license file changes
- License changes through the UI take effect immediately

## Implementation Details

### Test License Configuration
- **Test Email**: `pranay@example.com`
- **Recognition**: Automatic when key or email matches test email
- **Validation**: Always considered valid regardless of format
- **Functionality**: Identical to purchased license

### License Validation Rules
1. **No License**: All restricted operations blocked
2. **Test License**: All operations allowed
3. **Regular License**: Must be 6+ characters, all operations allowed
4. **Invalid License**: Less than 6 characters, operations blocked

### Restriction Points
The licensing system checks permissions at these points:
- Export dialog opening
- PDF paste operations
- PDF save operations
- Toolbar action states
- Menu item availability

This testing guide ensures you can thoroughly validate the licensing restrictions work correctly in both trial and licensed modes.
