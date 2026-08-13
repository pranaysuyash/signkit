"""Backend auto-start manager for hybrid architecture.

This module provides automatic backend management for cloud features
while maintaining offline-first operation for core functionality.
"""

from __future__ import annotations

import atexit
import hashlib
import hmac
import logging
import os
import secrets
import socket
import subprocess
import sys
import time
from threading import Thread
from pathlib import Path
from typing import Optional

LOG = logging.getLogger(__name__)


class BackendManager:
    """Manages optional backend service for cloud features."""
    
    def __init__(self, port: int = 8001, auto_start: bool = True):
        """Initialize backend manager.
        
        Args:
            port: Port to run backend on
            auto_start: Whether to automatically start backend
        """
        self.port = port
        self.auto_start = auto_start
        self.process: Optional[subprocess.Popen] = None
        self._available = False
        self._startup_attempts = 0
        self._max_startup_attempts = 3
        self._server_thread: Optional[Thread] = None
        self._health_token = secrets.token_urlsafe(32)
        from typing import Any as _Any
        self._server: _Any = None
        
        # Register cleanup on exit
        atexit.register(self.shutdown)
    
    def is_port_available(self, port: int) -> bool:
        """Check if a port is available for use.
        
        Args:
            port: Port number to check
            
        Returns:
            True if port is available, False otherwise
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                return result != 0  # Port is available if connection fails
        except Exception:
            return True  # Assume available if we can't check

    def _find_available_port(self, start: int = 8001, end: int = 8100) -> Optional[int]:
        """Find an available TCP port in the given range.

        Args:
            start: Starting port number (inclusive)
            end: Ending port number (inclusive)

        Returns:
            First available port number, or None if none found
        """
        for p in range(start, end + 1):
            if self.is_port_available(p):
                return p
        return None
    
    def find_backend_executable(self) -> Optional[str]:
        """Find the backend executable or script.
        
        Returns:
            Path to backend executable or None if not found
        """
        # Look for backend in common locations
        possible_paths = [
            # Development setup
            "backend/main.py",
            "../backend/main.py", 
            "backend/app/main.py",
            "../backend/app/main.py",
            # Packaged setup
            "backend/backend.exe",
            "backend/backend",
            # Virtual environment
            ".venv/Scripts/uvicorn.exe",
            ".venv/bin/uvicorn",
            "venv/Scripts/uvicorn.exe", 
            "venv/bin/uvicorn",
        ]
        
        for path in possible_paths:
            full_path = Path(path)
            if full_path.exists():
                LOG.debug(f"Found backend at: {full_path}")
                return str(full_path)
        
        # Try to find uvicorn in PATH
        try:
            result = subprocess.run(
                ["which", "uvicorn"] if sys.platform != "win32" else ["where", "uvicorn"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                LOG.debug(f"Found uvicorn in PATH: {result.stdout.strip()}")
                return "uvicorn"
        except Exception:
            pass
        
        LOG.warning("Backend executable not found")
        return None

    def _local_sqlite_url(self) -> str:
        """Return a user-writable SQLite URL for local fallback mode."""
        base = self._local_data_dir()
        db_path = os.path.join(base, "signature_extractor.db")
        return f"sqlite:///{db_path}"

    def _local_data_dir(self) -> str:
        """Return a user-writable application data directory."""
        override = os.environ.get("SIGNKIT_DATA_DIR")
        if override:
            os.makedirs(override, exist_ok=True)
            return override

        app_name = "SignKit"
        if sys.platform == "darwin":
            base = os.path.expanduser(f"~/Library/Application Support/{app_name}")
        elif sys.platform == "win32":
            base = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), app_name)
        else:
            base = os.path.expanduser(f"~/.local/share/{app_name}")
        os.makedirs(base, exist_ok=True)
        return base

    def _prepare_backend_env(self, env: dict[str, str]) -> dict[str, str]:
        """Prepare backend environment variables for local or production startup."""
        prepared = env.copy()
        prepared["SIGNKIT_RUNTIME_PROFILE"] = "local_companion"
        prepared["SIGNKIT_HEALTH_TOKEN"] = self._health_token
        sqlite_fallback = self._local_sqlite_url()

        # Preserve explicit production configuration, but make local startup work
        # even when DATABASE_URL is absent.
        if not prepared.get("DATABASE_URL"):
            prepared["DATABASE_URL"] = sqlite_fallback

        # Persist and provide a JWT secret if missing.
        if not prepared.get("JWT_SECRET"):
            base_dir = self._local_data_dir()
            secrets_dir = os.path.join(base_dir, "secrets")
            os.makedirs(secrets_dir, exist_ok=True)
            secret_file = os.path.join(secrets_dir, "jwt_secret")
            try:
                if os.path.exists(secret_file):
                    with open(secret_file, "r", encoding="utf-8") as f:
                        secret = f.read().strip()
                else:
                    import secrets as _secrets
                    secret = _secrets.token_hex(32)
                    with open(secret_file, "w", encoding="utf-8") as f:
                        f.write(secret)
                prepared["JWT_SECRET"] = secret
            except Exception as e:
                LOG.warning(f"Failed to persist JWT secret, generating ephemeral one: {e}")
                try:
                    import secrets as _secrets
                    prepared["JWT_SECRET"] = _secrets.token_hex(32)
                except Exception:
                    pass

        return prepared
    
    def start(self) -> bool:
        """Start backend as subprocess (non-blocking).
        
        Returns:
            True if backend is available (started or already running), False for offline mode
        """
        if not self.auto_start:
            LOG.debug("Auto-start disabled, checking if backend is already running")
            return self.is_available()
        
        # Check if already running
        if self.process and self.process.poll() is None:
            if self.is_available():
                LOG.debug("Backend process already running and healthy")
                return True
            else:
                LOG.warning("Backend process running but not responding, restarting")
                self.shutdown()
        
        # Check if port is available; if not, try dynamic selection
        if not self.is_port_available(self.port):
            LOG.info(f"Port {self.port} is already in use, checking if it's our backend")
            if self.is_available():
                LOG.info("Backend already running on port, using existing instance")
                return True
            else:
                alt = self._find_available_port(self.port + 1, self.port + 100)
                if alt is not None:
                    LOG.info(f"Selected alternate backend port: {alt}")
                    self.port = alt
                else:
                    LOG.error(f"No available ports found near {self.port}")
                    return False
        
        # For packaged apps, prefer in-process server for reliability
        if getattr(sys, "frozen", False):
            LOG.info("Detected packaged app (frozen). Starting backend in-process thread.")
            return self._start_inprocess_server()

        # Find backend executable for development environment
        backend_path = self.find_backend_executable()
        if not backend_path:
            LOG.warning("Backend executable not found; attempting in-process server fallback")
            return self._start_inprocess_server()
        
        # Increment startup attempts
        self._startup_attempts += 1
        if self._startup_attempts > self._max_startup_attempts:
            LOG.error(f"Max startup attempts ({self._max_startup_attempts}) exceeded")
            return False
        
        try:
            LOG.info(f"Starting backend on port {self.port} (attempt {self._startup_attempts})")
            
            # Prepare command
            if backend_path.endswith('.py'):
                # Python script - use uvicorn
                cmd = [
                    sys.executable, "-m", "uvicorn",
                    "backend.app.main:app",
                    "--host", "127.0.0.1",
                    "--port", str(self.port),
                    "--log-level", "warning"
                ]
                cwd = None
            elif backend_path == "uvicorn":
                # Uvicorn in PATH
                cmd = [
                    "uvicorn",
                    "backend.app.main:app", 
                    "--host", "127.0.0.1",
                    "--port", str(self.port),
                    "--log-level", "warning"
                ]
                cwd = None
            else:
                # Executable
                cmd = [backend_path, "--port", str(self.port)]
                cwd = None

            # Prepare environment for subprocess with sane defaults in packaged app.
            env = self._prepare_backend_env(os.environ)
            
            # Start process
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
                env=env,
                creationflags=creation_flags
            )
            
            LOG.info(f"Backend process started with PID {self.process.pid}")
            
            # Wait for backend to become available (shorter timeout for better UX)
            max_wait = 3  # seconds - reduced from 10 for faster startup
            wait_interval = 0.2
            waited: float = 0.0
            
            while waited < max_wait:
                if self.is_available():
                    LOG.info(f"Backend started successfully after {waited:.1f}s")
                    self._available = True
                    return True
                
                # Check if process died
                if self.process.poll() is not None:
                    stdout, stderr = self.process.communicate()
                    LOG.error(f"Backend process died during startup:")
                    LOG.error(f"stdout: {stdout.decode()}")
                    LOG.error(f"stderr: {stderr.decode()}")
                    return False
                
                time.sleep(wait_interval)
                waited += wait_interval
            
            LOG.warning(f"Backend did not become available within {max_wait}s")
            return False
            
        except Exception as e:
            LOG.error(f"Failed to start backend: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if backend is currently available.
        
        Returns:
            True if backend is responding to health checks
        """
        try:
            import requests
            
            url = f"http://127.0.0.1:{self.port}/health"
            response = requests.get(
                url,
                headers={"X-SignKit-Health-Token": self._health_token},
                timeout=2,
            )

            if response.status_code == 200:
                payload = response.json()
                expected_proof = hmac.new(
                    self._health_token.encode("utf-8"),
                    b"signkit-health-v1:/health",
                    hashlib.sha256,
                ).hexdigest()
                if payload.get("health_proof") != expected_proof:
                    self._available = False
                    return False
                self._available = True
                return True
            else:
                self._available = False
                return False
                
        except Exception:
            self._available = False
            return False
    
    def shutdown(self) -> None:
        """Gracefully shutdown backend process."""
        # Stop in-process server first, if running
        if self._server is not None:
            try:
                LOG.info("Shutting down in-process backend server")
                # Signal server to exit and wait for thread
                try:
                    self._server.should_exit = True
                except Exception:
                    pass
                if self._server_thread and self._server_thread.is_alive():
                    self._server_thread.join(timeout=5)
                LOG.info("In-process backend server stopped")
            except Exception as e:
                LOG.error(f"Error stopping in-process server: {e}")
            finally:
                self._server = None
                self._server_thread = None

        if self.process:
            try:
                LOG.info("Shutting down backend process")
                
                # Try graceful termination first
                self.process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.process.wait(timeout=5)
                    LOG.info("Backend shut down gracefully")
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    LOG.warning("Backend did not shut down gracefully, forcing termination")
                    self.process.kill()
                    self.process.wait()
                    
            except Exception as e:
                LOG.error(f"Error shutting down backend: {e}")
            finally:
                self.process = None
                self._available = False
    
    def restart(self) -> bool:
        """Restart the backend process.
        
        Returns:
            True if restart successful, False otherwise
        """
        LOG.info("Restarting backend")
        self.shutdown()
        time.sleep(1)  # Brief pause
        return self.start()
    
    def get_status(self) -> dict:
        """Get current backend status information.
        
        Returns:
            Dictionary with status information
        """
        return {
            "available": self._available,
            "process_running": self.process is not None and self.process.poll() is None,
            "port": self.port,
            "auto_start": self.auto_start,
            "startup_attempts": self._startup_attempts,
            "pid": self.process.pid if self.process else None
        }

    def _start_inprocess_server(self) -> bool:
        """Start the FastAPI backend within the current process in a background thread.

        This approach is robust inside packaged apps where launching external
        interpreters or scripts may fail. We rely on bundled modules.
        """
        # If already started and healthy
        if self._server_thread and self._server_thread.is_alive():
            if self.is_available():
                return True

        try:
            import uvicorn  # type: ignore

            # Prepare a user-writable environment (same as subprocess branch)
            env = self._prepare_backend_env(dict(os.environ))
            os.environ["SIGNKIT_HEALTH_TOKEN"] = env["SIGNKIT_HEALTH_TOKEN"]
            os.environ["SIGNKIT_RUNTIME_PROFILE"] = env["SIGNKIT_RUNTIME_PROFILE"]

            config = uvicorn.Config(
                "backend.app.main:app",
                host="127.0.0.1",
                port=self.port,
                log_level="warning",
                workers=1,
                reload=False,
            )
            server = uvicorn.Server(config)
            self._server = server

            def _run_server():
                try:
                    server.run()
                except Exception as e:
                    LOG.error(f"In-process backend server error: {e}")

            t = Thread(target=_run_server, name="BackendServerThread", daemon=True)
            t.start()
            self._server_thread = t

            # Wait up to 3s for availability (reduced for faster startup)
            max_wait = 3
            waited = 0.0
            interval = 0.2
            while waited < max_wait:
                if self.is_available():
                    self._available = True
                    LOG.info("In-process backend started successfully")
                    return True
                time.sleep(interval)
                waited += interval

            LOG.warning("In-process backend did not become available within timeout")
            return False
        except Exception as e:
            LOG.error(f"Failed to start in-process backend: {e}")
            return False


def ensure_backend_available(backend_manager: BackendManager) -> str:
    """Ensure backend is available and return status.
    
    Args:
        backend_manager: BackendManager instance
        
    Returns:
        Status string: "online", "offline", or "starting"
    """
    if backend_manager.is_available():
        return "online"
    
    if backend_manager.auto_start:
        if backend_manager.start():
            return "online"
        else:
            return "offline"
    else:
        return "offline"
