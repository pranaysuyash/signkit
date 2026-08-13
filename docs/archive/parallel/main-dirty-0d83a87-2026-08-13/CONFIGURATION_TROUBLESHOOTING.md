# Configuration Troubleshooting Guide

This guide helps resolve common configuration issues with the Signature Extractor application.

## Quick Fixes

### 1. "JWT_SECRET is missing" Error

**Problem**: Backend fails to start with JWT_SECRET validation error.

**Solution**:
```bash
# Generate a secure JWT secret
openssl rand -hex 32

# Add to your .env file
echo "JWT_SECRET=your_generated_key_here" >> .env
```

### 2. "Database connection failed" Error

**Problem**: Cannot connect to database.

**Solutions**:

**For PostgreSQL (production or multi-user mode)**:
```env
# Make sure PostgreSQL is running
DATABASE_URL=postgresql://username:password@localhost:5432/signature_extractor

# Or use individual settings
DATABASE_HOSTNAME=localhost
DATABASE_PORT=5432
DATABASE_USERNAME=your_username
DATABASE_PASSWORD=your_password
DATABASE_NAME=signature_extractor
```

### 3. "Backend: Offline" in Desktop App

**Problem**: Desktop app shows backend as offline.

**Solutions**:

1. **Check backend is running**:
   ```bash
   # Start backend if not running
   uvicorn backend.app.main:app --host 127.0.0.1 --port 8001
   ```

2. **Check API_BASE_URL**:
   ```env
   # In .env file - must match backend port
   API_BASE_URL=http://127.0.0.1:8001
   ```

3. **Test backend health**:
   ```bash
   curl http://127.0.0.1:8001/health
   ```

**For local single-user development**:
```env
# SQLite fallback works for the backend and desktop app startup
DATABASE_URL=sqlite:///./signature_extractor.db
```

Notes:
- The desktop app can run fully offline for signature extraction.
- The backend supports SQLite for local testing and PostgreSQL for production/backend scaling.

### 4. "Invalid API_BASE_URL format" Error

**Problem**: Desktop app configuration validation fails.

**Solution**:
```env
# Correct format (include protocol and port)
API_BASE_URL=http://127.0.0.1:8001

# Wrong formats:
# API_BASE_URL=127.0.0.1:8001        # Missing protocol
# API_BASE_URL=http://localhost      # Missing port
```

## Configuration Validation

### Backend Validation

The backend validates configuration on startup and provides helpful error messages:

```python
# Example validation errors:
# - JWT_SECRET is missing or using example value
# - DATABASE_PASSWORD is missing or using example value  
# - DATABASE_PORT must be between 1-65535
```

### Desktop App Validation

The desktop app validates configuration and shows clear error messages:

```python
# Example validation errors:
# - Invalid API_BASE_URL format
# - Invalid LOG_LEVEL (must be DEBUG, INFO, WARNING, ERROR, CRITICAL)
# - Invalid UPDATES_URL format
```

## Environment-Specific Setup

### Development Environment

```env
# .env for development
JWT_SECRET=dev_secret_key_replace_in_production
API_BASE_URL=http://127.0.0.1:8001
DATABASE_URL=postgresql://username:password@localhost:5432/signature_extractor
DEBUG=true
LOG_LEVEL=DEBUG
```

### Production Environment

```env
# .env for production
JWT_SECRET=super_secure_production_key_32_bytes_hex
API_BASE_URL=https://api.yourapp.com
DATABASE_URL=postgresql://user:pass@prod-db:5432/signature_extractor
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### Docker Environment

```env
# .env for Docker
JWT_SECRET=docker_dev_secret_replace_me
API_BASE_URL=http://backend:8001
DATABASE_URL=postgresql://postgres:password@db:5432/signature_extractor
DEBUG=true
```

## Port Configuration

### Consistent Port Usage

The application uses **port 8001** consistently across all components:

- Backend server: `127.0.0.1:8001`
- Desktop app API calls: `http://127.0.0.1:8001`
- Health check: `http://127.0.0.1:8001/health`

### Changing the Port

If you need to use a different port:

1. **Update backend startup**:
   ```bash
   uvicorn backend.app.main:app --host 127.0.0.1 --port 8002
   ```

2. **Update desktop app config**:
   ```env
   API_BASE_URL=http://127.0.0.1:8002
   ```

3. **Update backend manager** (if using auto-start):
   ```python
   # In desktop_app/main.py
   backend_manager = BackendManager(port=8002, auto_start=True)
   ```

## Database Setup

### PostgreSQL Setup (production / multi-user backend)

1. **Install PostgreSQL**:
   ```bash
   # macOS
   brew install postgresql
   brew services start postgresql
   
   # Ubuntu
   sudo apt install postgresql postgresql-contrib
   sudo systemctl start postgresql
   ```

2. **Create database and user**:
   ```sql
   -- Connect as postgres user
   sudo -u postgres psql
   
   -- Create database and user
   CREATE DATABASE signature_extractor;
   CREATE USER your_username WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE signature_extractor TO your_username;
   ```

3. **Update configuration**:
   ```env
   DATABASE_URL=postgresql://your_username:your_password@localhost:5432/signature_extractor
   ```

## Common Error Messages

### "Configuration validation failed"

This error occurs when required configuration values are missing or invalid.

**Check**:
- `.env` file exists in project root
- All required variables are set
- No example values are being used
- Variable formats are correct

### "Cannot reach backend"

This error occurs when the desktop app cannot connect to the backend.

**Check**:
- Backend is running on the correct port
- `API_BASE_URL` matches backend address
- No firewall blocking the connection
- Backend health endpoint responds

### "Database connection failed"

This error occurs when the backend cannot connect to the database.

**Check**:
- Database server is running (for PostgreSQL)
- Database credentials are correct
- Database exists and is accessible

## Getting Help

If you're still having configuration issues:

1. **Check the logs**:
   - Backend logs: Console output or `app.log`
   - Desktop app logs: Console output

2. **Verify configuration**:
   ```bash
   # Check .env file exists and has content
   cat .env
   
   # Test backend health
   curl http://127.0.0.1:8001/health
   ```

3. **Reset to defaults**:
   ```bash
   # Start fresh with example configuration
   cp .env.example .env
   # Edit .env with your values
   ```

4. **Check documentation**:
   - [README.md](../README.md) - Main setup guide
   - [.env.example](../.env.example) - Configuration examples
   - [Help & Troubleshooting](HELP.md) - General troubleshooting
