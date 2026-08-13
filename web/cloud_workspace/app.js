const state = {
  token: window.localStorage.getItem("signkit_workspace_token"),
  templates: [],
  executions: [],
  localJobs: [],
  selectedId: null,
  transitionError: "",
  proofFixtures: null,
  proofMessage: "",
  documentInspections: {},
};

const PROOF_STATUS_TRANSITIONS = {
  received: {
    request_review: "ready_for_review",
    request_correction: "needs_correction",
    record_exception: "exception",
    cancel: "cancelled",
  },
  ready_for_review: {
    approve: "approved",
    request_review: "ready_for_review",
    request_correction: "needs_correction",
    record_exception: "exception",
    cancel: "cancelled",
  },
  needs_correction: {
    request_review: "ready_for_review",
    record_exception: "exception",
    cancel: "cancelled",
  },
  approved: {
    sign: "signed",
    record_exception: "exception",
    cancel: "cancelled",
  },
  signed: {
    export: "exported",
    record_exception: "exception",
    cancel: "cancelled",
  },
  exception: {
    retry_review: "ready_for_review",
    cancel: "cancelled",
  },
};

const PROOF_SYNTHETIC_EVENT_TEMPLATE = {
  mark_received: "Packet marked as received in control plane.",
  request_review: "Execution review requested by operator in synthetic proof run.",
  request_correction: "Correction request recorded to reopen review path.",
  approve: "Execution marked approved by operator in synthetic proof run.",
  sign: "Execution signature-stage marker reached in synthetic proof run.",
  export: "Execution exported with deterministic audit manifest in synthetic proof run.",
  record_exception: "Execution entered exception state in synthetic proof run.",
  retry_review: "Execution returned from exception to review-ready state in synthetic proof run.",
  cancel: "Execution cancelled by operator in synthetic proof run.",
};

const authShell = document.querySelector("#auth-shell");
const appShell = document.querySelector("#app-shell");
const authMessage = document.querySelector("#auth-message");
const executionMessage = document.querySelector("#execution-message");
const dialog = document.querySelector("#execution-dialog");
const proofMessage = document.querySelector("#proof-message");

function isSyntheticExecution(execution) {
  return Boolean(execution?.synthetic);
}

function isLocalDesktopExecution(execution) {
  return Boolean(execution?.local_desktop);
}

function eventTimestamp(base, offsetSeconds) {
  const baseDate = new Date(base);
  if (Number.isNaN(baseDate.getTime())) {
    return new Date().toISOString();
  }
  return new Date(baseDate.getTime() + offsetSeconds * 1000).toISOString();
}

function deriveNextSyntheticEvent(execution, action) {
  const nextStatus = PROOF_STATUS_TRANSITIONS[execution.status]?.[action];
  if (!nextStatus) {
    throw new Error(`Cannot apply synthetic action '${action}' from '${execution.status}'.`);
  }
  return nextStatus;
}

function normalizeProofExecution(raw) {
  const events = (raw.events || []).slice().map((event, index) => ({
    id: String(event.id || `${raw.id}-event-${String(index + 1).padStart(3, "0")}`),
    sequence: Number(event.sequence || index + 1),
    event_type: String(event.event_type || "system"),
    status_from: event.status_from ?? null,
    status_to: String(event.status_to),
    idem_key: event.idem_key ?? null,
    summary: String(event.summary || "Synthetic proof event."),
    created_at: String(event.created_at || new Date().toISOString()),
  }));

  return {
    ...raw,
    synthetic: true,
    events,
    passport: {
      passport_version: "1.0",
      execution_id: String(raw.id),
      topology: raw.topology || "local",
      source_of_truth: "synthetic_proof_fixture",
      owner_role: "proof_operator",
      template_code: String(raw.template_code || "contractdesk-stage1"),
      template_version: Number(raw.template_version || 1),
      aggregate_status: String(raw.status || "pending_review"),
      recovery_action: "proof_fixture_replay",
      data_boundary: "metadata_only_no_document_bytes",
      evidence: [],
    },
    topology: raw.topology || "local",
    notes: raw.notes ?? "",
    manifest: raw.manifest || null,
  };
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>'"]/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
  }[character]));
}

function readableStatus(status) {
  return status.replaceAll("_", " ");
}

function topologyLabel(topology) {
  const labels = {
    cloud: "cloud metadata-only",
    local: "local device",
    hybrid: "hybrid coordination",
  };
  return labels[topology] || topology;
}

function statusRecoveryGuidance(status) {
  const guidance = {
    needs_correction: "Correction requested. Resolve the issue out-of-band, then request review again so this packet can continue.",
    exception: "Execution entered exception mode. Fix the external blocker and retry review when the packet is ready.",
    signed: "Execution has reached the signing stage marker. Use export only after owner sign-off or recovery is complete.",
    exported: "Execution is finalized in control-plane terms. Keep the receipt trail for audit export packaging.",
  };
  return guidance[status] || "";
}

function statusActions(status) {
  const statusActionMap = {
    pending_review: [
      { action: "mark_received", label: "Mark packet received", primary: true },
      { action: "record_review", label: "Record reviewer approval", primary: true },
      { action: "cancel", label: "Cancel execution", primary: false },
    ],
    awaiting_participant: [
      { action: "record_participant_confirmation", label: "Record participant confirmation", primary: true },
      { action: "cancel", label: "Cancel execution", primary: false },
    ],
    received: [
      { action: "request_review", label: "Request review", primary: true },
      { action: "cancel", label: "Cancel execution", primary: false },
    ],
    ready_for_review: [
      { action: "approve", label: "Approve for signing prep", primary: true },
      { action: "request_correction", label: "Request correction", primary: false },
      { action: "record_exception", label: "Record exception", primary: false },
    ],
    needs_correction: [
      { action: "request_review", label: "Retry review request", primary: true },
      { action: "record_exception", label: "Record exception", primary: false },
    ],
    approved: [
      { action: "sign", label: "Mark signing stage complete", primary: true },
      { action: "record_exception", label: "Record exception", primary: false },
      { action: "cancel", label: "Cancel execution", primary: false },
    ],
    signed: [
      { action: "export", label: "Create audit manifest", primary: true },
      { action: "record_exception", label: "Record exception", primary: false },
      { action: "cancel", label: "Cancel execution", primary: false },
    ],
    exception: [
      { action: "retry_review", label: "Retry review", primary: true },
    ],
  };
  return statusActionMap[status] || [];
}

function actionButton(execution) {
  if (isLocalDesktopExecution(execution)) {
    if (execution.passport?.recovery_action !== "retry_local_job") {
      return "<p class=\"passport-empty-action\">No direct local action for this state.</p>";
    }
    return `<button class="primary-button" type="button" data-action="retry_local_job">Retry local execution <span>→</span></button>`;
  }
  const actions = statusActions(execution.status);
  if (!actions.length) {
    return "<p class=\"passport-empty-action\">No direct operator action for this state.</p>";
  }
  return actions
    .map(
      (item) => `
        <button class="${item.primary ? "primary-button" : "secondary-button"}" type="button" data-action="${item.action}">
          ${item.label} <span>→</span>
        </button>`
    )
    .join("");
}

function formatDate(value) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(new Date(value));
}

function manifestBlock(execution) {
  if (!execution.manifest) return "";
  return `
    <p class="eyebrow passport-manifest-heading">AUDIT MANIFEST (SYNTHETIC)</p>
    <div class="passport-manifest">
      <dl>
        <div><dt>Workflow</dt><dd>${escapeHtml(execution.manifest.workflow || "contractdesk-stage1")}</dd></div>
        <div><dt>Input hash</dt><dd>${escapeHtml(execution.manifest.input_hash || "n/a")}</dd></div>
        <div><dt>Decision policy</dt><dd>${escapeHtml(execution.manifest.decision_rules || "operator-confirmation only")}</dd></div>
      </dl>
      <p class="receipt-link">Fixture replay scope is deterministic and control-plane scoped.</p>
      <pre>${escapeHtml(JSON.stringify(execution.manifest, null, 2))}</pre>
    </div>
  `;
}

function applySyntheticTransition(execution, action) {
  const nextStatus = deriveNextSyntheticEvent(execution, action);
  const lastEvent = execution.events[execution.events.length - 1];
  const timestamp = eventTimestamp(lastEvent?.created_at || execution.updated_at || new Date().toISOString(), 60);
  const nextEvent = {
    id: `${execution.id}-event-${String(execution.events.length + 1).padStart(3, "0")}`,
    sequence: execution.events.length + 1,
    event_type: action,
    status_from: execution.status,
    status_to: nextStatus,
    idem_key: null,
    summary: PROOF_SYNTHETIC_EVENT_TEMPLATE[action],
    created_at: timestamp,
  };
  execution.status = nextStatus;
  execution.events.push(nextEvent);
  execution.updated_at = timestamp;
  if (execution.manifest) {
    execution.manifest.last_action = action;
    execution.manifest.last_status = nextStatus;
    if (nextStatus === "exported") {
      execution.manifest.last_exported_at = timestamp;
      execution.manifest.output = execution.manifest.output || {};
      execution.manifest.output.exported_at = timestamp;
      execution.manifest.output.state = "synthetic export complete";
    }
  }
  return execution;
}

async function loadProofFixtures() {
  if (state.proofFixtures) return state.proofFixtures;
  const response = await fetch("./proof-fixtures.json");
  if (!response.ok) {
    throw new Error("Synthetic proof fixture failed to load.");
  }
  state.proofFixtures = await response.json();
  return state.proofFixtures;
}

function seedSyntheticProofExecution() {
  return (state.proofFixtures?.executions || [])
    .filter((execution) => !state.executions.some((item) => item.id === execution.id))
    .map((execution) => normalizeProofExecution(execution));
}

function clearProofMessage() {
  state.proofMessage = "";
  renderProofMessage();
}

function setProofMessage(text) {
  state.proofMessage = text;
  renderProofMessage();
}

function renderProofMessage() {
  proofMessage.textContent = state.proofMessage;
}

function formatApiError(body) {
  const detail = body?.detail;
  if (typeof detail === "string" && detail.trim()) return detail;
  if (Array.isArray(detail)) {
    const messages = detail.map((item) => item?.msg).filter(Boolean);
    if (messages.length) return messages.join("; ");
  }
  if (detail && typeof detail === "object" && typeof detail.message === "string") {
    return detail.message;
  }
  return "The workspace could not complete that request.";
}

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  if (options.body && !(options.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }
  const response = await fetch(path, { ...options, headers });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(formatApiError(body));
    error.status = response.status;
    throw error;
  }
  return body;
}

function activateAuthTab(tab) {
  const isLogin = tab === "login";
  document.querySelector("#login-tab").classList.toggle("is-active", isLogin);
  document.querySelector("#register-tab").classList.toggle("is-active", !isLogin);
  document.querySelector("#login-form").classList.toggle("is-hidden", !isLogin);
  document.querySelector("#register-form").classList.toggle("is-hidden", isLogin);
  authMessage.textContent = "";
}

function setSession(token) {
  state.token = token;
  window.localStorage.setItem("signkit_workspace_token", token);
}

async function authenticate(form, register = false) {
  authMessage.textContent = "";
  const data = new FormData(form);
  const email = String(data.get("email") || "").trim();
  const password = String(data.get("password") || "");
  try {
    if (register) {
      await api("/auth/register", { method: "POST", body: JSON.stringify({ email, password }) });
    }
    const formBody = new URLSearchParams({ username: email, password });
    const result = await api("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formBody,
    });
    setSession(result.access_token);
    await openWorkspace();
  } catch (error) {
    authMessage.textContent = error.message;
  }
}

function selectedExecution() {
  return state.executions.find((execution) => execution.id === state.selectedId) || null;
}

function normalizeLocalJob(raw) {
  const passport = raw.passport || {};
  const events = (passport.evidence || []).map((event, index) => ({
    id: `${raw.job_id}-event-${index + 1}`,
    sequence: Number(event.sequence || index + 1),
    event_type: event.code || "local_workflow_event",
    status_from: event.state_from ?? null,
    status_to: event.state_to || raw.status,
    idem_key: null,
    summary: event.code || "Local workflow state recorded.",
    created_at: event.occurred_at || raw.updated_at,
  }));
  return {
    id: `local:${raw.job_id}`,
    job_id: raw.job_id,
    local_desktop: true,
    title: raw.title,
    status: raw.status,
    topology: "local",
    template_code: raw.template_code,
    template_version: raw.template_version,
    participant_name: "Local desktop operator",
    participant_email: "Kept on this device",
    reviewer_name: "Local workflow owner",
    reviewer_email: "Kept on this device",
    effective_date: null,
    notes: "Metadata-only projection from the local desktop workflow store.",
    created_at: raw.created_at,
    updated_at: raw.updated_at,
    events,
    passport,
  };
}

function hydrateDocumentInspectionResults(executions) {
  for (const execution of executions) {
    const success = (execution.events || []).find(
      (event) => event.event_type === "document_inspection" && event.result,
    );
    if (success?.result) {
      state.documentInspections[execution.id] = {
        ...success.result,
        receipt_id: success.result.receipt_id || success.id,
        replayed: false,
      };
    }
  }
}

function renderMetrics() {
  const active = state.executions.filter((execution) => !["completed", "cancelled"].includes(execution.status));
  document.querySelector("#metric-active").textContent = active.length;
  document.querySelector("#metric-review").textContent = state.executions.filter((execution) => ["pending_review", "needs_review", "retry", "failed"].includes(execution.status)).length;
  document.querySelector("#metric-completed").textContent = state.executions.filter((execution) => execution.status === "completed").length;
  document.querySelector("#execution-count").textContent = `${state.executions.length} packet${state.executions.length === 1 ? "" : "s"}`;
}

function renderExecutions() {
  const list = document.querySelector("#execution-list");
  if (!state.executions.length) {
    list.innerHTML = `<div class="empty-state"><div><strong>No packets in the register.</strong><br />Start from the HR onboarding template to make one responsible next action visible.</div></div>`;
    return;
  }
  list.innerHTML = state.executions.map((execution) => `
    <button class="execution-row ${execution.id === state.selectedId ? "is-selected" : ""}" type="button" data-execution-id="${execution.id}">
      <div><h3>${escapeHtml(execution.title)}</h3><p>${escapeHtml(execution.participant_name)} · reviewer: ${escapeHtml(execution.reviewer_name)} · effective ${formatDate(execution.effective_date)}</p></div>
      <span class="state-pill state-${escapeHtml(execution.status)}">${escapeHtml(readableStatus(execution.status))}</span>
    </button>
  `).join("");
  list.querySelectorAll("[data-execution-id]").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedId = button.dataset.executionId;
      renderExecutions();
      renderPassport();
    });
  });
}

function documentInspectionBlock(execution) {
  if (execution.synthetic || execution.local_desktop || execution.topology !== "local") return "";
  const result = state.documentInspections[execution.id];
  const failure = [...(execution.events || [])]
    .reverse()
    .find((event) => event.event_type === "document_inspection_failed" && event.result);
  const failureMarkup = failure?.result
    ? `<div class="document-inspection-result document-inspection-failure" role="alert">
        <strong>Inspection needs attention</strong>
        <span>${escapeHtml(failure.result.failure_code || "inspection_failed")}</span>
        <small>${escapeHtml(failure.result.operator_action || "Review the event receipt and retry when safe.")}</small>
      </div>`
    : "";
  const resultMarkup = result
    ? `<div class="document-inspection-result" role="status">
        <strong>Inspection receipt recorded</strong>
        <span>${escapeHtml(result.pages_processed)} page processed · ${escapeHtml(result.candidates?.length || 0)} candidate(s)</span>
        <code>${escapeHtml(result.input_sha256)}</code>
        <small>${result.replayed ? "Replayed from the same idempotency key." : "New isolated-worker result."} Source bytes were not retained.</small>
    </div>`
    : "";
  return `
    <section class="document-inspection">
      <p class="eyebrow">LOCAL COMPANION INSPECTION</p>
      <p>Submit one PDF to the local companion. PDFium runs in a disposable worker; the source bytes are deleted after inspection.</p>
      <form id="document-inspection-form" class="document-inspection-form">
        <label>PDF document<input name="file" type="file" accept="application/pdf,.pdf" required /></label>
        <button class="secondary-button" type="submit">Inspect locally <span>→</span></button>
      </form>
      ${resultMarkup}
      ${failureMarkup}
    </section>
  `;
}

async function inspectDocument(form) {
  const execution = selectedExecution();
  if (!execution) return;
  const data = new FormData(form);
  const file = data.get("file");
  if (!(file instanceof File) || !file.size) {
    state.transitionError = "Choose a PDF document before starting local inspection.";
    renderPassport();
    return;
  }
  const idempotencyKey = window.crypto?.randomUUID?.() || `document-${Date.now()}`;
  try {
    state.transitionError = "";
    const result = await api(
      `/workspace/executions/${execution.id}/document-inspections`,
      {
        method: "POST",
        headers: { "Idempotency-Key": idempotencyKey },
        body: data,
      },
    );
    state.documentInspections[execution.id] = result;
    renderPassport();
  } catch (error) {
    state.transitionError = error.message;
    renderPassport();
  }
}

function renderPassport() {
  const execution = selectedExecution();
  document.querySelector("#passport-empty").classList.toggle("is-hidden", Boolean(execution));
  const content = document.querySelector("#passport-content");
  content.classList.toggle("is-hidden", !execution);
  if (!execution) return;
  const passport = execution.passport || {};
  const guidance = statusRecoveryGuidance(execution.status);
  const feedback = state.transitionError
    ? `<p class="passport-feedback is-visible" role="status">${escapeHtml(state.transitionError)}</p>`
    : "";
  state.transitionError = "";
  content.innerHTML = `
    <p class="eyebrow">EXECUTION PASSPORT · ${escapeHtml(isLocalDesktopExecution(execution) ? "local desktop projection" : topologyLabel(execution.topology))}</p>
    <h2 class="passport-title">${escapeHtml(execution.title)}</h2>
    <span class="passport-status">${escapeHtml(readableStatus(execution.status))}</span>
    <dl class="passport-facts">
      <div><dt>Template lineage</dt><dd>${escapeHtml(execution.template_code)} / v${execution.template_version}</dd></div>
      <div><dt>Current boundary</dt><dd>${passport.data_boundary === "metadata_only_no_document_bytes" ? "Metadata-only browser record; document bytes remain outside this surface." : "Passport boundary unavailable; no document data is present here."}</dd></div>
      <div><dt>Source of truth</dt><dd>${passport.source_of_truth === "workspace_control_plane" ? "Browser workspace control plane" : escapeHtml(passport.source_of_truth || "Passport unavailable from workspace API")}</dd></div>
      <div><dt>Passport status</dt><dd>${escapeHtml(passport.aggregate_status || execution.status || "pending_review")}</dd></div>
      <div><dt>Receipt reference</dt><dd>${escapeHtml(passport.output_reference || "Not available")}</dd></div>
      <div><dt>Recovery</dt><dd>${escapeHtml(passport.recovery_action || "Recovery guidance unavailable")}</dd></div>
      <div><dt>Participant</dt><dd>${escapeHtml(execution.participant_name)}<br />${escapeHtml(execution.participant_email)}</dd></div>
      <div><dt>Reviewer</dt><dd>${escapeHtml(execution.reviewer_name)}<br />${escapeHtml(execution.reviewer_email)}</dd></div>
      <div><dt>Effective date</dt><dd>${formatDate(execution.effective_date)}</dd></div>
    </dl>
    ${guidance ? `<div class="passport-guide"><p>${escapeHtml(guidance)}</p></div>` : ""}
    ${documentInspectionBlock(execution)}
    <div class="passport-actions">${actionButton(execution)}</div>
    ${feedback}
    <p class="eyebrow receipt-heading">CHRONOLOGICAL RECEIPT</p>
    <ol class="receipt">${execution.events.map((event) => `<li>${escapeHtml(event.summary)}<small>#${event.sequence} · ${formatDate(event.created_at)}</small></li>`).join("")}</ol>
    ${manifestBlock(execution)}
  `;
  content.querySelectorAll("[data-action]").forEach((button) => {
    button.addEventListener("click", () => transitionExecution(button.dataset.action));
  });
  const inspectionForm = content.querySelector("#document-inspection-form");
  if (inspectionForm) {
    inspectionForm.addEventListener("submit", (event) => {
      event.preventDefault();
      inspectDocument(event.currentTarget);
    });
  }
}

function renderTemplates() {
  const list = document.querySelector("#template-list");
  list.innerHTML = state.templates.map((template) => `
    <article class="template-card">
      <p class="eyebrow">${escapeHtml(template.vertical)} · V${template.version}</p>
      <h3>${escapeHtml(template.name)}</h3>
      <p>${escapeHtml(template.description)}</p>
      <footer><span>${template.document_count} packet elements · ${template.steps.length} actions</span><button type="button" data-template-code="${template.code}">Use template →</button></footer>
    </article>
  `).join("");
  list.querySelectorAll("[data-template-code]").forEach((button) => {
    button.addEventListener("click", () => openExecutionDialog(button.dataset.templateCode));
  });
}

async function refreshWorkspace() {
  const [templates, executions, localJobs] = await Promise.all([
    api("/workspace/templates"),
    api("/workspace/executions"),
    api("/workspace/local-jobs").catch((error) => {
      if (error.status === 404) return [];
      throw error;
    }),
  ]);
  state.templates = templates;
  state.localJobs = localJobs.map(normalizeLocalJob);
  const preservedSynthetic = state.executions.filter((execution) => execution.synthetic);
  const merged = [...state.localJobs, ...executions];
  for (const execution of preservedSynthetic) {
    const exists = merged.some((item) => item.id === execution.id);
    if (!exists) {
      merged.unshift(execution);
    }
  }
  state.executions = merged;
  hydrateDocumentInspectionResults(state.executions);
  if (!selectedExecution() && executions.length) state.selectedId = executions[0].id;
  renderMetrics();
  renderExecutions();
  renderPassport();
  renderTemplates();
}

async function openWorkspace() {
  authShell.classList.add("is-hidden");
  appShell.classList.remove("is-hidden");
  try {
    await refreshWorkspace();
  } catch (error) {
    window.localStorage.removeItem("signkit_workspace_token");
    state.token = null;
    appShell.classList.add("is-hidden");
    authShell.classList.remove("is-hidden");
    authMessage.textContent = "Your session could not be opened. Please sign in again.";
  }
}

function openExecutionDialog(templateCode) {
  const template = state.templates.find((item) => item.code === templateCode) || state.templates[0];
  if (!template) return;
  document.querySelector("#template-code").value = template.code;
  document.querySelector("#template-description").textContent = `${template.description} ${template.privacy_note}`;
  executionMessage.textContent = "";
  dialog.showModal();
}

async function submitExecution(form) {
  executionMessage.textContent = "";
  const data = Object.fromEntries(new FormData(form).entries());
  if (!data.effective_date) data.effective_date = null;
  if (!data.notes) data.notes = null;
  try {
    const execution = await api("/workspace/executions", { method: "POST", body: JSON.stringify(data) });
    state.selectedId = execution.id;
    form.reset();
    dialog.close();
    await refreshWorkspace();
  } catch (error) {
    executionMessage.textContent = error.message;
  }
}

async function transitionExecution(action) {
  const execution = selectedExecution();
  if (!execution) return;
  try {
    state.transitionError = "";
    if (isSyntheticExecution(execution)) {
      applySyntheticTransition(execution, action);
      renderMetrics();
      renderExecutions();
      renderPassport();
      return;
    }
    if (isLocalDesktopExecution(execution)) {
      await api(`/workspace/local-jobs/${execution.job_id}/retry`, { method: "POST" });
      await refreshWorkspace();
      return;
    }
    await api(`/workspace/executions/${execution.id}/transitions`, { method: "POST", body: JSON.stringify({ action }) });
    await refreshWorkspace();
  } catch (error) {
    state.transitionError = error.message;
    renderPassport();
  }
}

async function loadProofScenario() {
  try {
    state.proofMessage = "";
    clearProofMessage();
    if (!state.proofFixtures) {
      await loadProofFixtures();
    }
    const seeded = seedSyntheticProofExecution();
    if (!seeded.length) {
      setProofMessage("Synthetic proof packet already loaded.");
      return;
    }
    state.executions = [...seeded, ...state.executions];
    if (!state.selectedId) {
      state.selectedId = seeded[0].id;
    } else {
      state.selectedId = seeded[0].id;
    }
    renderMetrics();
    renderExecutions();
    renderPassport();
    setProofMessage("Loaded deterministic ContractDesk proof packet and manifest.");
  } catch (error) {
    setProofMessage(error.message);
  }
}

document.querySelector("#login-tab").addEventListener("click", () => activateAuthTab("login"));
document.querySelector("#register-tab").addEventListener("click", () => activateAuthTab("register"));
document.querySelector("#login-form").addEventListener("submit", (event) => { event.preventDefault(); authenticate(event.currentTarget); });
document.querySelector("#register-form").addEventListener("submit", (event) => { event.preventDefault(); authenticate(event.currentTarget, true); });
document.querySelector("#new-execution").addEventListener("click", () => openExecutionDialog(state.templates[0]?.code));
document.querySelector("#load-proof-fixture").addEventListener("click", loadProofScenario);
document.querySelector("#close-dialog").addEventListener("click", () => dialog.close());
document.querySelector("#cancel-dialog").addEventListener("click", () => dialog.close());
document.querySelector("#execution-form").addEventListener("submit", (event) => { event.preventDefault(); submitExecution(event.currentTarget); });
document.querySelector("#sign-out").addEventListener("click", () => { state.token = null; state.executions = []; state.selectedId = null; window.localStorage.removeItem("signkit_workspace_token"); appShell.classList.add("is-hidden"); authShell.classList.remove("is-hidden"); activateAuthTab("login"); });

if (state.token) openWorkspace();
if (proofMessage) {
  renderProofMessage();
}
