# Controlled Workflow Module Interfaces (v1)

## Data models

### `ControlledSigningRecipe`

- `recipe_id: str`
- `version: int`
- `status: Literal['draft','approved','active','suspended','revoked']`
- `name: str`
- `document_matcher: MatcherConfig`
- `field_bindings: list[FieldBinding]`
- `input_folder: FolderConfig`
- `output_folder: FolderConfig`
- `review_folder: FolderConfig | None`
- `authorization_policy: GrantPolicy`
- `created_by: str`
- `approved_by: str | None`
- `created_at: datetime`
- `approved_at: datetime | None`
- `content_hash: str`

### `FieldBinding`

- `field_id: str`
- `field_kind: Literal['signature','initials','date','text']`
- `signer_role: str`
- `signature_asset_id: str`
- `page_selector: int`
- `anchor_type: Literal['bbox','anchor_text','manual']`
- `anchor_definition: dict[str, str | float | int]`
- `relative_geometry: dict[str, float]`
- `required: bool = True`
- `expected_count: int = 1`
- `manual_fallback_allowed: bool = False`

### `ExecutionGrant`

- `grant_id: str`
- `recipe_id: str`
- `recipe_version: int`
- `approver_subject: str`
- `runner_roles: list[str]`
- `allowed_assets: list[str]`
- `input_folder_id: str`
- `output_folder_id: str`
- `matcher_modes: list[Literal['exact','family']]`
- `max_jobs: int | None`
- `expires_at: datetime | None`
- `is_active: bool`
- `revoked_at: datetime | None`

### `WorkflowJob`

- `job_id: str`
- `input_path_ref: str`
- `input_fingerprint: str`
- `recipe_id: str`
- `recipe_version: int`
- `grant_id: str | None`
- `match_class: Literal['exact','family','review_only']`
- `state: WorkflowState`
- `attempts: int`
- `max_attempts: int`
- `last_error_code: str | None`
- `created_at: datetime`
- `updated_at: datetime`

### `JobEvent`

- `event_id: str`
- `job_id: str`
- `state_from: WorkflowState | None`
- `state_to: WorkflowState`
- `actor: str`
- `code: str`
- `message: str | None`
- `occurred_at: datetime`

## Public interfaces

### `authorization.py`

- `require_authorization(job: WorkflowJob, subject: str, requested_action: str) -> GrantDecision`
- `create_grant(recipe_id: str, policy: GrantPolicy, runner: str) -> ExecutionGrant`
- `revoke_grant(grant_id: str, actor: str, reason: str) -> None`
- `is_grant_valid(grant: ExecutionGrant, now: datetime | None = None) -> bool`

### `matcher.py`

- `class MatchResult(NamedTuple)`
  - `match_class: Literal['exact','family','review_only']`
  - `confidence: float`
  - `evidence: dict[str, str]`
- `evaluate_match(recipe: ControlledSigningRecipe, pdf_path: str) -> MatchResult`

### `engine.py`

- `class WorkflowEngine`
  - `start() -> None`
  - `stop() -> None`
  - `enqueue_path(pdf_path: str, recipe_id: str | None = None) -> WorkflowJob`
  - `run_job(job_id: str) -> WorkflowJob`
  - `transition(job_id: str, to_state: WorkflowState, actor: str, code: str, message: str | None = None) -> WorkflowJob`

### `folder_monitor.py`

- `class FolderMonitor`
  - `start() -> None`
  - `stop() -> None`
  - `scan_once() -> list[str]`
  - `is_stable(path: str) -> bool`

### `verifier.py`

- `verify_output(input_pdf: str, output_pdf: str, expected_state: dict[str, object]) -> VerifyResult`
- `compute_hash(path: str) -> str`

### `pdf/signer.py`

- `class SignResult(NamedTuple)`
  - `ok: bool`
  - `output_path: str | None`
  - `error_code: str | None`
  - `error_message: str | None`
- `sign_pdf(input_pdf: str, output_pdf: str, placements: list[dict], *, atomic: bool = True) -> SignResult`

## Failure code taxonomy (starter)

- `ERR_AUTH_MISSING`
- `ERR_AUTH_EXPIRED`
- `ERR_AUTH_REVOKED`
- `ERR_MATCH_NONE`
- `ERR_MATCH_AMBIGUOUS`
- `ERR_FOLDER_LOCKED`
- `ERR_IO_UNSTABLE`
- `ERR_SIGNING_FAILED`
- `ERR_VERIFY_MISMATCH`
- `ERR_OUTPUT_EXISTS`
- `ERR_OUTPUT_IO`

## Persistence contract assumptions

- All ids are stable UUIDv4 strings.
- All timestamps are UTC ISO-8601.
- Receipt payloads include recipe + grant + job + event lineage but never raw signature binaries.
