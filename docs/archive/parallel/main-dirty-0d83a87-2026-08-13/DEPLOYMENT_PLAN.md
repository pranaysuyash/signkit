# Deployment Plan — Signature Extractor

## Objectives
- Ship a desktop-first product (macOS/Windows/Linux) with a local FastAPI backend and optional cloud mode.
- Keep installs frictionless, private by default, and updatable without breaking user workflows.

## Artifacts
- Desktop app binary (PyInstaller or Nuitka)
- Backend container image for optional cloud (FastAPI + PostgreSQL)
- Documentation and release notes per version

## Environments
- Local (Developer): venv, `uvicorn backend.app.main:app --reload --port 8001`, `python -m desktop_app.main`
- Staging (Optional): Cloud instance or container environment mirroring prod
- Production: Signed desktop binaries; optional deployed backend/cloud services

## Desktop Packaging
- Tooling: PyInstaller (baseline), evaluate Nuitka for perf/size later
- Targets: macOS universal2, Windows x64, Linux AppImage
- Outputs: Single executable + assets; include Qt libs and required Python runtime

### macOS
- Build: `pyinstaller --windowed --name "Signature Extractor" desktop_app/main.py`
- Codesign: Sign with Developer ID; notarize with Apple; staple tickets
- Gatekeeper: Verify launch on a clean machine
- Auto-update: Evaluate Sparkle via a lightweight wrapper or custom updater that polls GitHub Releases

### Windows
- Build: PyInstaller onefile/onedir; test launch speed and DLL packaging
- Code signing: EV certificate recommended; sign via signtool
- Updater: WinSparkle/Squirrel.Windows or custom updater (MSI + delta updates)

### Linux
- Build: AppImage for portability; also evaluate .deb/.rpm if demand
- Signing: GPG signatures for downloads

### Packaging QA
- Launch on clean VMs for each OS
- Verify: open/upload/select/preview/export; rotate (when implemented); library persistence
- Size targets: <100MB if possible; document known limits

## Backend Deployment (Optional Cloud)
- Container: Docker image with FastAPI
- DB: PostgreSQL via `DATABASE_URL`
- Hosting options: Fly.io, Railway, DO App Platform, AWS/GCP/Azure (container services)
- Health and uptime: `/health` endpoint; liveness/readiness if using k8s
- SSL: Terminate at load balancer or use Traefik/Caddy for local deployments

### Config & Secrets
- .env (local): `JWT_SECRET`, `DATABASE_URL` (PostgreSQL), ports
- Secrets in cloud: platform secret manager; never commit
- CORS: Restrict to local desktop or trusted origins

## CI/CD
- CI: GitHub Actions
  - Lint/type-check (if configured), basic backend tests
  - Build backend container on tags
  - Build desktop installers on tags (macOS/Windows/Linux jobs)
- CD: Publish installers to GitHub Releases; optionally push container to registry
- Release notes: CHANGELOG-driven; auto-generate from PR labels

## Versioning & Release Cadence
- Semantic versioning (MAJOR.MINOR.PATCH)
- Cadence: Biweekly minor updates; hotfix as needed
- Deprecation policy: Document feature removals with one minor version notice

## Telemetry & Monitoring
- Desktop: Opt-in analytics (Plausible/PostHog) respecting privacy-first stance
- Backend: Structured logs; Sentry for error reporting; request timing middleware

## Security & Compliance
- Local-first: Default to local processing; no uploads to cloud unless user opts in
- Data at rest: Local library lives under user directory; document path and backup guidance
- Code signing: Required for trust and reduced AV false positives
- Dependencies: Pin and scan (pip-audit); update quarterly or on CVEs

## Rollback Strategy
- Keep previous installers available under Releases
- Desktop: Updater should allow “Revert to previous version” if issues are reported
- Backend: Blue/green or canary deployments for cloud; quick rollback to previous image

## Distribution
- Website landing page with direct download links
- Product Hunt and community posts at launch
- Optional package managers: winget/choco (Windows), Homebrew (macOS), apt repo (Linux) in later phase
