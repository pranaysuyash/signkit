# SignKit Design and Delivery Notes

Date: 2026-07-25  
Scope: macOS premium runtime + shared engine, with PySide-based standard app remaining for Windows/Linux.

## Product Position

- **Shared execution core (all platforms):** extraction, template storage, vault-backed signatures, PDF signing path, workflow models/jobs, and authorization layer.
- **Platform split:**
  - **Windows / Linux (Standard):** `desktop_app/main.py` + `standard` profile.
  - **macOS Premium:** `desktop_app/main_macos_premium.py` + `mac-premium` profile.
- **Policy rule:** no parallel signing engines. macOS premium is a *UI/profile skin* plus entitlement defaults on the same shared engine.

## Profile Contract

`desktop_app/launch_profile.py`

- `standard`:
  - `premium_ui=False`
  - default `plan=starter`
  - window title/app defaults to SignKit
  - onboarding shows pricing upgrade CTA cards
- `mac-premium`:
  - `premium_ui=True`
  - `default_plan_id="team"`
  - window title/app defaults to SignKit Premium
  - onboarding hides upgrade matrix and shows premium profile context

## Personas and Screen Priorities

1. **Solo operator / solo legal admin**
   - Goal: quick extraction + repeatable placements.
   - Default: Starter flow, manual execution.

2. **Ops team lead**
   - Goal: recurring folder signing with role controls.
   - Default: Team flow.
   - Screens: Workflow Console, Grant Manager, Recipe Builder.

3. **Compliance-minded operations**
   - Goal: controlled execution policy, review/retry controls, auditability.
   - Recommended: Business policy extensions where implemented (still staged for next release).

## Pricing and Screens

- Starter: local/manual-first behavior, one-user repeatability.
- Team: recurring folder workflow controls, grants, review lane, retry/quarantine.
- Business: high-volume + policy-heavy operations (future extensions).

Onboarding behavior:
- Standard profile keeps the plan/upgrade matrix visible.
- macOS Premium profile uses a premium-context onboarding section and no upgrade matrix.

## Core Workflow Screens (Implementation Target)

- Locked workflow states (standard): locked tabs with explicit upgrade/CTA.
- Premium workflow screens:
  - **Workflow Dashboard** (jobs + state summary + controls)
  - **Workflow Grants** (policy/scoped execution)
  - **Recipe Builder** (input/output/review folder triplet + role-role bindings)

## Folder Triplet Standard

- `RecipeBuilder` requires:
  - unsigned docs folder
  - signed output folder
  - optional review folder
- Validation enforces folder existence and separation to avoid nested overwrite/collision behavior.

## Quality Guardrails

- Fail-closed behavior for missing/invalid authorization checks.
- Explicit status text and upgrade messaging in locked workflow screens.
- Test coverage path:
  - profile resolution
  - bootstrap wiring
  - build entrypoint/profile mapping
  - purchase-plan propagation

## Open Work

- Desktop native mac visual polish (`DESIGN.md` already present) continues in line with Apple's affordances and accessibility.
- Business/enterprise pricing extensions, legal workflow boundaries, and explicit evidence export remain future releases.
