const { test, expect } = require('@playwright/test');

const workspaceUrl = 'http://127.0.0.1:8872/workspace-app/index.html';

test.describe('ContractDesk workspace control plane', () => {
  test('loads the real proof surface with explicit local and cloud boundaries', async ({ page }) => {
    const response = await page.goto(workspaceUrl, { waitUntil: 'networkidle' });

    expect(response).not.toBeNull();
    expect(response.status()).toBe(200);

    await expect(page.locator('body')).toContainText('SignKit Workspace');
    await expect(page.locator('body')).toContainText(/local[- ]companion/i);
    await expect(page.locator('body')).toContainText(/metadata-only/i);
    await expect(page.locator('body')).toContainText(/deletes source bytes|source bytes after/i);
  });
});
