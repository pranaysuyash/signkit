# Signature Extractor - Project Structure

This document outlines the organized folder structure of the Signature Extractor project.

## 📁 Project Organization

### 🚀 **Essential Application Code**
- **`backend/`** - FastAPI backend server (database, API, processing)
- **`desktop_app/`** - PySide6 desktop application (UI, logic, processing)
- **`flows/`** - Workflow and automation configurations

### 📚 **Documentation**
- **`docs/`** - All documentation including:
  - User guides and installation instructions
  - API documentation and technical specs
  - Business strategy and launch planning
  - Gumroad setup and marketing materials
  - Privacy policy and legal documentation

### 🎨 **Web & Marketing**
- **`web/`** - Web-related assets:
  - Demo animations and HTML files
  - Landing page variations and templates
  - Interactive demos and prototypes

- **`marketing/`** - Marketing and design strategy:
  - `landing-pages/` - Landing page design strategy and documentation
  - Various landing page approaches (Claude, ZAI, Grok, Codex, etc.)
  - Design strategy documents and implementation guides

### ⚙️ **Development & Build**
- **`build-tools/`** - Build configuration and scripts:
  - PyInstaller specifications
  - Build automation scripts
  - Build requirements and dependencies

- **`tests/`** - Test suites and testing utilities
- **`scripts/`** - Automation and utility scripts
- **`tools/`** - Development tools and utilities

### 📄 **Legal & Business**
- **`legal/`** - Legal documents:
  - Privacy Policy
  - Terms of Service
  - EULA (End User License Agreement)

- **`assets/`** - Static assets:
  - Images and screenshots
  - Demo documents
  - Visual assets for marketing

### 🔧 **Runtime & Logs**
- **`logs/`** - Application logs and debug files
- **`uploads/`** - User upload storage (for backend testing)
- **`build/`** - Build artifacts and compiled files
- **`dist/`** - Distribution packages (built executables)

### 🛠️ **Development Environment**
- **`.venv/`** - Python virtual environment
- **`venv/`** - Alternative virtual environment
- **`.vscode/`** - VS Code configuration
- **`.mypy_cache/`** - Type checking cache
- **`.pytest_cache/`** - Test runner cache

### 📸 **Debug & Testing**
- **`screenshots_debug/`** - Debug screenshots and test images

### ⚙️ **Configuration**
- **`.env.example`** - Environment configuration template
- **`.env`** - Local environment configuration (not in git)
- **`.gitignore`** - Git ignore patterns
- **`.github/`** - GitHub workflows and templates

## 🎯 **Quick Start Guide**

### For Development:
```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Start backend
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8001

# 4. Run desktop app
python -m desktop_app.main
```

### For Building:
```bash
# 1. Install build requirements
pip install -r build-tools/requirements-build.txt

# 2. Build application
python build-tools/build.py

# 3. Find builds in dist/ directory
ls dist/
```

### For Documentation:
```bash
# View main documentation
open docs/README.md

# View installation guide
open docs/INSTALLATION_GUIDE.md

# View launch readiness
open docs/LAUNCH_READINESS_REPORT.md
```

## 📋 **Key Files**

### Configuration:
- **`.env.example`** - Environment variables template
- **`docs/README.md`** - Main project documentation

### Application Entry Points:
- **`desktop_app/main.py`** - Desktop application entry point
- **`backend/app/main.py`** - Backend API entry point

### Build & Distribution:
- **`build-tools/build.py`** - Build automation script
- **`build-tools/signature_extractor.spec`** - PyInstaller configuration

### Legal:
- **`legal/PRIVACY_POLICY.md`** - Privacy policy
- **`legal/TERMS_OF_SERVICE.md`** - Terms of service
- **`legal/EULA.md` - End user license agreement

## 🎨 **Demo & Marketing**

### Web Demos:
- **`web/demo-animation.html`** - Main CSS animation demo
- **`web/signature-extraction-demo.html`** - Interactive demo
- **`web/landing_pages/`** - Various landing page designs

### Marketing Assets:
- **`docs/GUMROAD_COMPLETE_GUIDE.md`** - Complete Gumroad setup
- **`docs/STRATEGIC_BUSINESS_ANALYSIS.md`** - Business strategy
- **`assets/`** - Images and visual assets

## 🧹 **Clean Project Benefits**

1. **Easy Navigation**: Logical folder organization
2. **Clear Separation**: Code, docs, assets, and tools separated
3. **Scalable Structure**: Easy to add new features or assets
4. **Professional Layout**: Clean, maintainable project structure
5. **Development Ready**: All necessary tools and configurations organized

## 📝 **File Organization Logic**

- **Core Application**: `backend/`, `desktop_app/`, `flows/`
- **Documentation**: `docs/` (all documentation consolidated)
- **Web Assets**: `web/` (HTML, demos, landing pages)
- **Legal**: `legal/` (all legal documents)
- **Build Tools**: `build-tools/` (build scripts and configs)
- **Assets**: `assets/` (images, documents, media)
- **Development**: `tests/`, `scripts/`, `tools/`
- **Runtime**: `logs/`, `uploads/`, `build/`, `dist/`

This structure keeps the root directory clean while maintaining easy access to all project components.