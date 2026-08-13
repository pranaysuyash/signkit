#!/usr/bin/env node

/**
 * Reproducible local browser proof for the canonical product surface.
 *
 * This deliberately uses a real Playwright browser context so reduced-motion
 * evidence is not inferred from CSS source inspection alone. It does not start
 * a server, create an account, or contact a hosted service.
 */

import { pathToFileURL } from "node:url";

const playwrightModule = process.env.SIGNKIT_PLAYWRIGHT_MODULE
  || "/Users/pranay/Projects/skills/testing/playwright-skill/node_modules/playwright/index.js";
const playwright = await import(pathToFileURL(playwrightModule).href);
const { chromium } = playwright.default || playwright;

const landingBaseUrl = (process.env.SIGNKIT_LANDING_BASE_URL || "http://127.0.0.1:8080").replace(/\/$/, "");
const workspaceBaseUrl = (process.env.SIGNKIT_WORKSPACE_BASE_URL || "http://127.0.0.1:8001").replace(/\/$/, "");
const viewports = [
  { name: "desktop", width: 1440, height: 900 },
  { name: "touch", width: 390, height: 844 },
  { name: "narrow", width: 320, height: 844 },
];

function assertCondition(condition, message) {
  if (!condition) throw new Error(message);
}

async function pageErrors(page) {
  const errors = [];
  const onPageError = (error) => errors.push(`pageerror: ${error.message}`);
  const onConsole = (message) => {
    if (message.type() === "error") errors.push(`console: ${message.text()}`);
  };
  page.on("pageerror", onPageError);
  page.on("console", onConsole);
  return { errors, onPageError, onConsole };
}

async function verifyLanding(browser, viewport) {
  const context = await browser.newContext({ viewport, reducedMotion: "reduce" });
  const page = await context.newPage();
  const capture = await pageErrors(page);
  try {
    await page.goto(`${landingBaseUrl}/`, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(150);
    const base = await page.evaluate(() => {
      const button = document.querySelector(".button");
      const media = window.matchMedia("(prefers-reduced-motion: reduce)");
      return {
        title: document.title,
        main: Boolean(document.querySelector("main#main-content")),
        skipLink: {
          href: document.querySelector(".skip-link")?.getAttribute("href") || "",
          text: document.querySelector(".skip-link")?.textContent.trim() || "",
        },
        primaryCtaHref: document.querySelector("#local-workspace-link")?.href || "",
        stateRail: {
          label: document.querySelector('[role="tablist"]')?.getAttribute("aria-label") || "",
          names: [...document.querySelectorAll('[role="tab"]')].map((tab) => tab.textContent.trim()),
        },
        overflow: document.documentElement.scrollWidth > window.innerWidth,
        reducedMotion: media.matches,
        scrollBehavior: getComputedStyle(document.documentElement).scrollBehavior,
        transitionDuration: button ? getComputedStyle(button).transitionDuration : null,
        tabCount: document.querySelectorAll("[data-completion-step]").length,
        workspaceLinks: [...document.querySelectorAll("[data-local-workspace]")].map((link) => link.href),
        checkoutState: document.documentElement.dataset.checkoutState,
        gumroadHref: document.querySelector('[data-checkout-provider="gumroad"]:not(html)')?.href || "",
      };
    });
    assertCondition(base.title === "SignKit | Document registration studio", `${viewport.name}: unexpected title`);
    assertCondition(base.main, `${viewport.name}: main landmark missing`);
    assertCondition(base.skipLink.href === "#main-content", `${viewport.name}: skip link target is missing`);
    assertCondition(base.skipLink.text === "Skip to content", `${viewport.name}: skip link label is missing`);
    assertCondition(base.primaryCtaHref === `${workspaceBaseUrl}/workspace-app/`, `${viewport.name}: primary workspace CTA is not canonical`);
    assertCondition(base.stateRail.label === "Document preparation states", `${viewport.name}: state rail label is missing`);
    assertCondition(base.stateRail.names.join("|") === "01 Source|02 Mark|03 Clean|04 Place|05 Ready", `${viewport.name}: state labels are incomplete`);
    assertCondition(!base.overflow, `${viewport.name}: horizontal overflow detected`);
    assertCondition(base.reducedMotion, `${viewport.name}: reduced-motion media query not active`);
    assertCondition(base.scrollBehavior === "auto", `${viewport.name}: reduced-motion scroll behavior not reduced`);
    assertCondition(Number.parseFloat(base.transitionDuration) <= 0.001, `${viewport.name}: transition duration was not reduced`);
    assertCondition(base.tabCount === 5, `${viewport.name}: expected five workflow states, got ${base.tabCount}`);
    assertCondition(base.workspaceLinks.length === 2, `${viewport.name}: local workspace links are incomplete`);
    assertCondition(base.workspaceLinks.every((href) => href === `${workspaceBaseUrl}/workspace-app/`), `${viewport.name}: workspace handoff is not canonical`);
    assertCondition(base.checkoutState === "gumroad-primary", `${viewport.name}: checkout fallback state is not explicit`);
    assertCondition(base.gumroadHref === "https://pranaysuyash.gumroad.com/l/signkit-v1", `${viewport.name}: fallback checkout is not actionable`);

    await page.locator(".skip-link").focus();
    const skipFocus = await page.evaluate(() => ({
      active: document.activeElement?.classList.contains("skip-link"),
      transform: getComputedStyle(document.querySelector(".skip-link")).transform,
    }));
    assertCondition(skipFocus.active, `${viewport.name}: skip link cannot receive focus`);
    assertCondition(skipFocus.transform !== "none" && !skipFocus.transform.endsWith("-180%"), `${viewport.name}: skip link focus treatment is not visible`);

    const source = page.locator('[data-completion-step="source"]');
    await source.focus();
    await page.keyboard.press("ArrowRight");
    const keyboardState = await page.evaluate(() => ({
      status: document.querySelector("#completion-status")?.textContent,
      active: document.activeElement?.getAttribute("data-completion-step"),
    }));
    assertCondition(keyboardState.status === "MARK EXTRACTED", `${viewport.name}: keyboard state did not advance`);
    assertCondition(keyboardState.active === "mark", `${viewport.name}: keyboard focus did not follow state`);

    await page.locator('[data-completion-step="clean"]').click();
    const pointerState = await page.locator("#completion-status").textContent();
    assertCondition(pointerState?.trim() === "MARK CLEAN", `${viewport.name}: pointer state did not bind`);

    assertCondition(capture.errors.length === 0, `${viewport.name}: browser errors: ${capture.errors.join("; ")}`);
    return { viewport, base, keyboardState, pointerState: pointerState.trim(), errors: capture.errors };
  } finally {
    page.off("pageerror", capture.onPageError);
    page.off("console", capture.onConsole);
    await context.close();
  }
}

async function verifyWorkspace(browser) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: "reduce" });
  const page = await context.newPage();
  const capture = await pageErrors(page);
  try {
    const response = await page.goto(`${workspaceBaseUrl}/workspace-app/`, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(150);
    const result = await page.evaluate(() => ({
      title: document.title,
      status: document.querySelector("#trust-boundary")?.textContent.trim() || "",
      overflow: document.documentElement.scrollWidth > window.innerWidth,
      authShell: Boolean(document.querySelector("#auth-shell")),
      appShell: Boolean(document.querySelector("#app-shell")),
    }));
    assertCondition(response?.status() === 200, `workspace: expected 200, got ${response?.status()}`);
    assertCondition(result.title === "SignKit Workspace", "workspace: unexpected title");
    assertCondition(/metadata-first|not a signing claim/i.test(result.status), "workspace: boundary copy missing");
    assertCondition(!result.overflow, "workspace: horizontal overflow detected");
    assertCondition(result.authShell && result.appShell, "workspace: auth/app shell contract missing");
    assertCondition(capture.errors.length === 0, `workspace: browser errors: ${capture.errors.join("; ")}`);
    return { viewport: { width: 390, height: 844 }, status: response.status(), result, errors: capture.errors };
  } finally {
    page.off("pageerror", capture.onPageError);
    page.off("console", capture.onConsole);
    await context.close();
  }
}

const browser = await chromium.launch({ channel: "chrome", headless: true });
try {
  const landing = [];
  for (const viewport of viewports) landing.push(await verifyLanding(browser, viewport));
  const workspace = await verifyWorkspace(browser);
  console.log(JSON.stringify({ status: "pass", landing, workspace }, null, 2));
} finally {
  await browser.close();
}
