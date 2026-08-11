import { createRequire } from "node:module";
import { mkdirSync, writeFileSync, appendFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { firefox } = require("/Users/pranay/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright");
const runDir = dirname(fileURLToPath(import.meta.url));
const screenshots = join(runDir, "screenshots");
const logPath = join(runDir, "final_script_log.txt");
const url = "http://127.0.0.1:4176/web/concepts/2026-07-31-customer-work-experience/index.html";
mkdirSync(screenshots, { recursive: true });
writeFileSync(logPath, "");
const log = (step, message) => {
  const line = `step ${step} action: ${message}\n`;
  appendFileSync(logPath, line);
  process.stdout.write(line);
};

const errors = [];
const browser = await firefox.launch({ headless: true });
try {
  const context = await browser.newContext({ viewport: { width: 1280, height: 1800 } });
  const page = await context.newPage();
  page.on("console", (message) => { if (message.type() === "error") errors.push(`console ${message.type()}: ${message.text()}`); });
  page.on("pageerror", (error) => errors.push(`pageerror: ${error.message}`));

  await page.goto(url, { waitUntil: "networkidle" });
  await page.getByRole("heading", { name: "Get the document right." }).waitFor();
  await page.screenshot({ path: join(screenshots, "final_execution_1_open_customer_hero.png") });
  const pageText = await page.locator("body").innerText();
  const forbidden = ["topology", "proof gate", "Legal and HR are the proving ground", "Cloud", "Hybrid"];
  const present = forbidden.filter((term) => pageText.toLowerCase().includes(term.toLowerCase()));
  if (present.length) throw new Error(`Internal strategy language visible: ${present.join(", ")}`);
  if (await page.title() !== "SignKit | Get the document right") throw new Error(`Unexpected title: ${await page.title()}`);
  log(1, "opened customer-facing concept; title and public-language guard passed; hero screenshot saved");

  const workflow = page.getByRole("region", { name: "Follow the work, one clear step at a time." });
  await workflow.scrollIntoViewIfNeeded();
  const pdfTab = page.getByRole("tab", { name: "03 Continue in the PDF" });
  await pdfTab.click();
  await page.waitForTimeout(280);
  const selected = await pdfTab.getAttribute("aria-selected");
  const image = page.locator("#workflow-image");
  const alt = await image.getAttribute("alt");
  const caption = await page.locator("#workflow-caption").innerText();
  if (selected !== "true" || alt !== "Current SignKit PDF workspace with a completed sample workflow" || !caption.toLowerCase().includes("completed sample workflow")) {
    throw new Error(`Workflow selection did not update: selected=${selected}, alt=${alt}, caption=${caption}`);
  }
  await page.screenshot({ path: join(screenshots, "final_execution_2_pdf_workflow_selected.png") });
  log(2, "selected current completed-PDF workflow state; selected tab, accessible image label, caption, and screenshot verified");

  if (errors.length) throw new Error(errors.join("; "));
  log(3, "verified no browser console or page errors after interaction");
  appendFileSync(logPath, "\nFINAL_RESPONSE: Customer-facing concept opened, visual evidence captured, PDF workflow interaction verified, and no console errors observed.\n");
} finally {
  await browser.close();
}
