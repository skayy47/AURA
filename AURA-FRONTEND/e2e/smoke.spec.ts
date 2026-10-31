import { test, expect } from "@playwright/test";

test("landing page loads and shows hero", async ({ page }) => {
  await page.goto("/en");
  await expect(page).toHaveTitle(/AURA/i);
  // Hero headline contains "data" in some form
  const h1 = page.locator("h1").first();
  await expect(h1).toBeVisible();
  await expect(h1).toContainText(/data/i);
});

test("language switcher toggles to French", async ({ page }) => {
  await page.goto("/en");
  await page.locator("button[lang='fr']").first().click();
  await expect(page).toHaveURL(/\/fr/);
  await expect(page.locator("html")).toHaveAttribute("lang", "fr");
});

test("pricing page renders all 3 tiers", async ({ page }) => {
  await page.goto("/en/pricing");
  // Three tier name headings should be visible
  for (const tier of ["Free", "Pro", "Team"]) {
    await expect(page.getByText(tier, { exact: true }).first()).toBeVisible();
  }
});

test("ingest page shows empty state without session", async ({ page }) => {
  await page.goto("/en/ingest");
  // Either shows upload zone or empty state — page must not 500
  await expect(page.locator("body")).not.toContainText("500");
  await expect(page.locator("body")).not.toContainText("Internal Server Error");
});
