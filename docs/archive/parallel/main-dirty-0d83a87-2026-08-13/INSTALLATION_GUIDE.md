# Installation Guide

This guide covers installing Signature Extractor on different platforms and provides troubleshooting for common installation issues.

## System Requirements

### Minimum Requirements

- **Operating System**:
  - macOS 10.15 (Catalina) or later
  - Windows 10 (64-bit) or later
  - Ubuntu 20.04 LTS or equivalent
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 500MB available disk space
- **Processor**: 64-bit processor (ARM64 or x86_64)

### Recommended Requirements

- **Operating System**: Latest stable version
- **Memory**: 8GB RAM or more
- **Storage**: 1GB available disk space
- **Processor**: Multi-core processor for large image processing

## Installation Methods

### Method 1: Download Pre-built Binary (Recommended)

#### macOS Installation

1. **Download** the macOS DMG or ZIP file from Gumroad
2. **Open** the downloaded file
3. **Drag** SignatureExtractor.app to your Applications folder
4. **First Launch**:
   - Right-click on SignatureExtractor.app and select "Open"
   - Click "Open" in the security dialog (this is required for unsigned apps)
   - Grant necessary permissions when prompted

#### Windows Installation

1. **Download** the Windows ZIP file from Gumroad
2. **Extract** the ZIP file to a location of your choice
3. **Run** SignatureExtractor.exe
4. **Windows Defender** may show a warning - click "More info" then "Run anyway"
5. **Create Shortcut** (optional):
   - Right-click on SignatureExtractor.exe
   - Select "Send to" → "Desktop (create shortcut)"

#### Linux Installation

1. **Download** the Linux AppImage or TAR file from Gumroad
2. **Make executable**:
   ```bash
   chmod +x SignatureExtractor.AppImage
   ```
3. **Run** the application:
   ```bash
   ./SignatureExtractor.AppImage
   ```
4. **Optional**: Install to system:
   ```bash
   sudo cp SignatureExtractor.AppImage /usr/local/bin/signature-extractor
   ```

### Method 2: Build from Source (Advanced)

#### Prerequisites

Install the required dependencies:

```bash
# Clone the repository
git clone https://github.com/your-username/signature-extractor-app.git
cd signature-extractor-app

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-build.txt
```

#### Build Commands

```bash
# Build for current platform
python build.py

# Build with debug output
python build.py --debug

# Build console version (for troubleshooting)
python build.py --console

# Create installer scripts
python build.py --create-scripts
```

## First Launch Setup

### Configuration Setup

1. **Environment Configuration**:

   - Copy `.env.example` to `.env` in the installation directory
   - Generate a secure JWT secret: `openssl rand -hex 32`
   - Update the `.env` file with your JWT secret

2. **Backend Configuration**:

   - The application will attempt to start the backend automatically
   - If running in offline mode, core features will still work
   - Check the status bar for backend availability

3. **License Activation**:
   - Launch the application
   - Go to **License** → **Enter License Key...**
   - Enter your license key from Gumroad
   - The application will validate and activate your license

### Testing Your Installation

1. **Basic Test**:

   - Open an image file (PNG or JPEG)
   - Make a selection using the rectangle tool
   - Preview the extracted signature
   - Try the basic image processing features

2. **License Test**:

   - Test export functionality (PNG, JPG export)
   - Test PDF operations if you have PDF files
   - Verify all features are unlocked

3. **Backend Test**:
   - Check if backend is running (status bar should show "Online")
   - Test saving to library
   - Verify session management works

## Troubleshooting

### Common Issues

#### macOS Issues

**"App can't be opened because Apple cannot check it for malicious software"**

- Solution: Right-click the app → "Open" → "Open" in the dialog
- Alternative: Go to System Preferences → Security & Privacy → General → "Allow apps downloaded from: App Store and identified developers" → Click "Allow Anyway"

**App crashes on launch**

- Check System Console.app for crash logs
- Try running from Terminal: `/Applications/SignatureExtractor.app/Contents/MacOS/SignatureExtractor`
- Ensure macOS is up to date

#### Windows Issues

**"Windows protected your PC" warning**

- Click "More info" → "Run anyway"
- Add exception to Windows Defender if needed

**Missing DLL errors**

- Install Microsoft Visual C++ Redistributable
- Ensure all Windows updates are installed

**Application won't start**

- Run as Administrator
- Check Event Viewer for error logs
- Try compatibility mode (Windows 8)

#### Linux Issues

**Permission denied**

```bash
chmod +x SignatureExtractor.AppImage
```

**Missing libraries**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install libgl1-mesa-glx libxcb-xinerama0

# Fedora
sudo dnf install mesa-libGL libXinerama

# Arch Linux
sudo pacman -S mesa libxinerama
```

**AppImage doesn't run**

```bash
# Extract and run
./SignatureExtractor.AppImage --appimage-extract
./squashfs-root/AppRun
```

### Performance Issues

**Slow performance with large images**

- Reduce image size before processing
- Close other applications
- Increase RAM if possible
- Use the "Fit" view instead of "100%" zoom

**Memory errors**

- The application automatically limits memory usage
- Restart the application if it becomes slow
- Check available disk space for temporary files

### Network Issues

**Backend won't start**

- Check if port 8001 is available
- Try running backend manually:
  ```bash
  uvicorn backend.app.main:app --host 127.0.0.1 --port 8001
  ```
- Check firewall settings

**License validation fails**

- Ensure internet connection is active
- Check license key spelling
- Contact support if issues persist

## Advanced Configuration

### Environment Variables

Create or edit `.env` file:

```env
# Required settings
JWT_SECRET=your_secure_32_byte_hex_key_here
API_BASE_URL=http://127.0.0.1:8001
DATABASE_URL=postgresql://username:password@localhost:5432/signature_extractor

# Optional settings
LOG_LEVEL=INFO
DEBUG=false
ENABLE_ANALYTICS=false
```

### Backend Configuration

**Manual Backend Start**:

```bash
cd /path/to/signature-extractor-app
source .venv/bin/activate
uvicorn backend.app.main:app --host 127.0.0.1 --port 8001
```

**Database Configuration**:

- Backend requires PostgreSQL: set `DATABASE_URL=postgresql://user:pass@localhost:5432/dbname`

### Custom Installation Paths

**Portable Installation**:

- Extract the application to any folder
- All data is stored in the application directory
- No registry entries or system files are modified

**Network Installation**:

- Share the application folder on network drive
- Multiple users can run from same installation
- Each user gets separate data directory

## Updates and Maintenance

### Updating the Application

1. **Download** the latest version from Gumroad
2. **Backup** your current configuration and license
3. **Replace** the application files
4. **Restore** your configuration files if needed

### Data Backup

**Backup Location**:

- macOS: `~/Library/Application Support/SignatureExtractor/`
- Windows: `%APPDATA%/SignatureExtractor/`
- Linux: `~/.local/share/SignatureExtractor/`

**Backup Files**:

- `license.json` - Your license information
- `library/` - Your saved signatures and documents

### Uninstallation

**macOS**:

- Drag SignatureExtractor.app to Trash
- Remove data folder: `~/Library/Application Support/SignatureExtractor/`

**Windows**:

- Delete the application folder
- Remove data folder: `%APPDATA%/SignatureExtractor/`

**Linux**:

- Delete the AppImage or application folder
- Remove data folder: `~/.local/share/SignatureExtractor/`

## Support

### Getting Help

- **Documentation**: https://signatureextractor.app/docs
- **FAQ**: https://signatureextractor.app/faq
- **Email Support**: support@signkit.work
- **Community Forum**: https://community.signatureextractor.app

### Reporting Issues

When reporting issues, please include:

- Operating system and version
- Application version
- Step-by-step reproduction steps
- Any error messages or logs
- Screenshot if applicable

### Diagnostic Information

The application can generate diagnostic information:

1. Go to **Help** → **Generate Diagnostic Report**
2. Save the report file
3. Include it when contacting support

This installation guide should help you get Signature Extractor running on your system. If you encounter issues not covered here, please don't hesitate to contact our support team.
