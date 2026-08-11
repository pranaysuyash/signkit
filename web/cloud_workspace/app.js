const state = {
  token: window.localStorage.getItem("signkit_workspace_token"),
  templates: [],
  executions: [],
  selectedId: null,
};

const authShell = document.querySelector("#auth-shell");
const appShell = document.querySelector("#app-shell");
const authMessage = document.querySelector("#auth-message");
const executionMessage = document.querySelector("#execution-message");
const dialog = document.querySelector("#execution-dialog");

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>'"]/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
  }[character]));
}

function readableStatus(status) {
  return status.replaceAll("_", " ");
}

function formatDate(value) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(new Date(value));
}

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  if (options.body && !headers["Content-Type"]) headers["Content-Type"] = "application/json";
  const response = await fetch(path, { ...options, headers });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || "The workspace could not complete that request.");
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

function renderMetrics() {
  const active = state.executions.filter((execution) => !["completed", "cancelled"].includes(execution.status));
  document.querySelector("#metric-active").textContent = active.length;
  document.querySelector("#metric-review").textContent = state.executions.filter((execution) => execution.status === "pending_review").length;
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

function actionButton(execution) {
  if (execution.status === "pending_review") {
    return `<button class="primary-button" type="button" data-action="record_review">Record reviewer approval <span>→</span></button>`;
  }
  if (execution.status === "awaiting_participant") {
    return `<button class="primary-button" type="button" data-action="record_participant_confirmation">Record participant confirmation <span>→</span></button>`;
  }
  return "";
}

function renderPassport() {
  const execution = selectedExecution();
  document.querySelector("#passport-empty").classList.toggle("is-hidden", Boolean(execution));
  const content = document.querySelector("#passport-content");
  content.classList.toggle("is-hidden", !execution);
  if (!execution) return;
  content.innerHTML = `
    <p class="eyebrow">EXECUTION PASSPORT · ${escapeHtml(execution.topology)}</p>
    <h2 class="passport-title">${escapeHtml(execution.title)}</h2>
    <span class="passport-status">${escapeHtml(readableStatus(execution.status))}</span>
    <dl class="passport-facts">
      <div><dt>Template lineage</dt><dd>${escapeHtml(execution.template_code)} / v${execution.template_version}</dd></div>
      <div><dt>Participant</dt><dd>${escapeHtml(execution.participant_name)}<br />${escapeHtml(execution.participant_email)}</dd></div>
      <div><dt>Reviewer</dt><dd>${escapeHtml(execution.reviewer_name)}<br />${escapeHtml(execution.reviewer_email)}</dd></div>
      <div><dt>Effective date</dt><dd>${formatDate(execution.effective_date)}</dd></div>
    </dl>
    <div class="passport-actions">${actionButton(execution)}${!["completed", "cancelled"].includes(execution.status) ? `<button class="secondary-button" type="button" data-action="cancel">Cancel execution</button>` : ""}</div>
    <p class="eyebrow receipt-heading">CHRONOLOGICAL RECEIPT</p>
    <ol class="receipt">${execution.events.map((event) => `<li>${escapeHtml(event.summary)}<small>#${event.sequence} · ${formatDate(event.created_at)}</small></li>`).join("")}</ol>
  `;
  content.querySelectorAll("[data-action]").forEach((button) => {
    button.addEventListener("click", () => transitionExecution(button.dataset.action));
  });
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
  const [templates, executions] = await Promise.all([api("/workspace/templates"), api("/workspace/executions")]);
  state.templates = templates;
  state.executions = executions;
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
    await api(`/workspace/executions/${execution.id}/transitions`, { method: "POST", body: JSON.stringify({ action }) });
    await refreshWorkspace();
  } catch (error) {
    window.alert(error.message);
  }
}

document.querySelector("#login-tab").addEventListener("click", () => activateAuthTab("login"));
document.querySelector("#register-tab").addEventListener("click", () => activateAuthTab("register"));
document.querySelector("#login-form").addEventListener("submit", (event) => { event.preventDefault(); authenticate(event.currentTarget); });
document.querySelector("#register-form").addEventListener("submit", (event) => { event.preventDefault(); authenticate(event.currentTarget, true); });
document.querySelector("#new-execution").addEventListener("click", () => openExecutionDialog(state.templates[0]?.code));
document.querySelector("#close-dialog").addEventListener("click", () => dialog.close());
document.querySelector("#cancel-dialog").addEventListener("click", () => dialog.close());
document.querySelector("#execution-form").addEventListener("submit", (event) => { event.preventDefault(); submitExecution(event.currentTarget); });
document.querySelector("#sign-out").addEventListener("click", () => { state.token = null; state.executions = []; state.selectedId = null; window.localStorage.removeItem("signkit_workspace_token"); appShell.classList.add("is-hidden"); authShell.classList.remove("is-hidden"); activateAuthTab("login"); });

if (state.token) openWorkspace();
