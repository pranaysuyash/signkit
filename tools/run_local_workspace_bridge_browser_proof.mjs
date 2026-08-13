#!/usr/bin/env node

/**
 * Real-browser proof for the local desktop passport bridge.
 *
 * The proof uses a disposable local data root supplied by SIGNKIT_DATA_DIR,
 * creates a temporary local account, seeds one metadata-only desktop job bound
 * to that account, and exercises the browser workspace through the real local
 * HTTP server. It never contacts a hosted service and never sends document
 * bytes to the browser workspace.
 */

import { spawnSync } from "node:child_process";
import { pathToFileURL } from "node:url";

const root = new URL("../", new URL("./", import.meta.url));
const seedTool = new URL("./seed_local_bridge_job.py", import.meta.url);
const playwrightModule = process.env.SIGNKIT_PLAYWRIGHT_MODULE
  || "/Users/pranay/Projects/skills/testing/playwright-skill/node_modules/playwright/index.js";
const playwright = await import(pathToFileURL(playwrightModule).href);
const { chromium } = playwright.default || playwright;
const workspaceBaseUrl = (process.env.SIGNKIT_WORKSPACE_BASE_URL || "http://127.0.0.1:8001").replace(/\/$/, "");
const pythonBin = process.env.SIGNKIT_PYTHON || "./.venv/bin/python";
const receiptReference = process.env.SIGNKIT_LOCAL_RECEIPT_REFERENCE || "sha256:local-bridge-proof-receipt";

function assertCondition(condition, message) {
  if (!condition) throw new Error(message);
}

async function jsonRequest(path, options = {}) {
  const response = await fetch(`${workspaceBaseUrl}${path}`, options);
  const body = await response.json().catch(() => ({}));
  return { response, body };
}

function tokenSubject(token) {
  const segment = token.split(".")[1];
  return JSON.parse(Buffer.from(segment, "base64url").toString("utf8")).sub;
}

async function createProofAccount() {
  const suffix = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  const email = `local-bridge-proof-${suffix}@example.com`;
  const password = "local-bridge-proof-password";
  const registration = await jsonRequest("/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  assertCondition(registration.response.status === 201, `bridge: registration failed (${registration.response.status})`);
  const login = await jsonRequest("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ username: email, password }),
  });
  assertCondition(login.response.status === 200, `bridge: login failed (${login.response.status})`);
  return { email, password, token: login.body.access_token, subject: tokenSubject(login.body.access_token) };
}

function seedJob(subject) {
  assertCondition(process.env.SIGNKIT_DATA_DIR, "bridge: SIGNKIT_DATA_DIR is required for disposable proof data");
  const result = spawnSync(
    pythonBin,
    [seedTool.pathname, "--subject", subject, "--data-dir", process.env.SIGNKIT_DATA_DIR, "--receipt-reference", receiptReference],
    { cwd: root.pathname, env: process.env, encoding: "utf8" },
  );
  assertCondition(result.status === 0, `bridge: seed failed (${result.stderr || result.stdout})`);
  return JSON.parse(result.stdout.trim());
}

async function main() {
  const account = await createProofAccount();
  const seeded = seedJob(account.subject);
  const unauthenticated = await jsonRequest(`/workspace/local-jobs/${seeded.job_id}`);
  assertCondition(unauthenticated.response.status === 401, "bridge: unauthenticated direct URL did not fail closed");
  const missing = await jsonRequest(`/workspace/local-jobs/not-a-real-job`, {
    headers: { Authorization: `Bearer ${account.token}` },
  });
  assertCondition(missing.response.status === 404, "bridge: missing job did not return 404");
  const listed = await jsonRequest("/workspace/local-jobs", {
    headers: { Authorization: `Bearer ${account.token}` },
  });
  assertCondition(listed.response.status === 200, "bridge: authenticated local job list failed");
  assertCondition(listed.body.length === 1, `bridge: expected one seeded job, got ${listed.body.length}`);
  const serialized = JSON.stringify(listed.body);
  assertCondition(!serialized.includes("private-source-document.pdf"), "bridge: private source path leaked in API payload");
  assertCondition(!serialized.includes("private source path"), "bridge: private event message leaked in API payload");

  const browser = await chromium.launch({ channel: "chrome", headless: true });
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: "reduce" });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (error) => errors.push(`pageerror: ${error.message}`));
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(`console: ${message.text()}`);
  });
  try {
    await page.goto(`${workspaceBaseUrl}/workspace-app/`, { waitUntil: "domcontentloaded" });
    await page.locator("#login-email").fill(account.email);
    await page.locator("#login-password").fill(account.password);
    await page.getByRole("button", { name: /Open workspace/ }).click();
    await page.locator("#app-shell:not(.is-hidden)").waitFor();
    const localRow = page.locator(".execution-row", { hasText: "Local desktop execution" });
    await localRow.waitFor();
    await localRow.click();
    const beforeRetry = await page.locator("#passport-content").textContent();
    assertCondition(/local_workflow_store/i.test(beforeRetry), "bridge: local source of truth is not visible");
    assertCondition(beforeRetry.includes(`local-receipt:${receiptReference}`), "bridge: opaque receipt reference is not visible");
    assertCondition(/Retry local execution/i.test(beforeRetry), "bridge: retry action is not visible");
    assertCondition(!beforeRetry.includes("private-source-document.pdf"), "bridge: private path leaked in browser UI");
    const [retryResponse] = await Promise.all([
      page.waitForResponse((response) => response.url().includes(`/workspace/local-jobs/${seeded.job_id}/retry`) && response.status() === 200),
      page.getByRole("button", { name: /Retry local execution/ }).click(),
    ]);
    const retryPayload = await retryResponse.json();
    assertCondition(retryPayload.status === "failed", `bridge: retry did not produce failed recovery state (${retryPayload.status})`);
    assertCondition(retryPayload.passport?.recovery_action === "inspect_local_job", "bridge: retry response did not expose canonical recovery action");
    await page.waitForTimeout(250);
    const afterRetry = await page.locator("#passport-content").textContent();
    assertCondition(/inspect_local_job/i.test(afterRetry), `bridge: missing source recovery state is not visible: ${afterRetry}`);
    assertCondition(!afterRetry.includes("private-source-document.pdf"), "bridge: private path leaked after retry");
    assertCondition(errors.length === 0, `bridge: browser errors: ${errors.join("; ")}`);
    process.stdout.write(`${JSON.stringify({
      status: "pass",
      job_id: seeded.job_id,
      unauthenticated_status: unauthenticated.response.status,
      missing_status: missing.response.status,
      before_retry_contains_local_source: /local_workflow_store/i.test(beforeRetry),
      before_retry_contains_receipt_reference: beforeRetry.includes(`local-receipt:${receiptReference}`),
      receipt_reference: receiptReference,
      after_retry_contains_recovery: /inspect_local_job/i.test(afterRetry),
      retry_status: retryPayload.status,
      document_bytes_in_browser_workspace: false,
      browser_errors: errors,
    }, null, 2)}\n`);
  } finally {
    await context.close();
    await browser.close();
  }
}

await main();
