import { expect, test, type Page } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

const env = fs.readFileSync(path.resolve("..", ".env"), "utf8");
const password = env.match(/^DEMO_PASSWORD=(.*)$/m)?.[1]?.trim();
const gallery = path.resolve("..", "docs", "screenshots", "portfolio");

const routes = [
  ["01-dashboard-en", "/"],
  ["02-governance", "/governance"],
  ["03-policies", "/policies"],
  ["05-risks", "/risks"],
  ["06-assessments", "/assessments"],
  ["08-findings", "/findings"],
  ["09-gaps", "/gaps"],
  ["10-remediation", "/remediation"],
  ["11-evidence", "/evidence"],
  ["12-privacy", "/privacy"],
  ["13-vendors", "/vendors"],
  ["14-incidents", "/incidents"],
  ["15-continuity", "/continuity"],
  ["16-training", "/training"],
  ["17-acknowledgements", "/acknowledgements"],
  ["18-data-inventory", "/data-inventory"],
  ["19-sources", "/sources"],
  ["20-audit", "/audit"],
  ["21-reports", "/reports"],
  ["22-settings-roles", "/settings"],
] as const;

async function capture(page: Page, name: string) {
  await page.locator("main").waitFor({ state: "visible" });
  await page.waitForLoadState("networkidle");
  await page.screenshot({
    path: path.join(gallery, `${name}.png`),
    fullPage: true,
  });
}

test("capture a complete read-only portfolio gallery", async ({ page, browser }) => {
  test.skip(!password, "Run local bootstrap and start both services");
  fs.mkdirSync(gallery, { recursive: true });

  await page.goto("/");
  await page.screenshot({
    path: path.join(gallery, "00-login-ar.png"),
    fullPage: true,
  });
  await page.getByRole("button", { name: "العربية / English" }).click();
  await page.screenshot({
    path: path.join(gallery, "00-login-en.png"),
    fullPage: true,
  });
  await page.getByRole("button", { name: "العربية / English" }).click();
  await page.locator("input[name=username]").fill("owner");
  await page.locator("input[name=password]").fill(password!);
  await page.locator("button.primary").click();
  await expect(
    page.getByRole("heading", { name: "مركز قيادة الحوكمة" }),
  ).toBeVisible();
  await page.screenshot({
    path: path.join(gallery, "01-dashboard-ar.png"),
    fullPage: true,
  });
  await page.getByRole("button", { name: "English", exact: true }).click();

  for (const [name, route] of routes) {
    await page.goto(route);
    await capture(page, name);
  }

  await page.goto("/policies");
  await page.locator("tbody tr").first().click();
  await expect(page.locator(".record-view")).toBeVisible();
  await capture(page, "04-policy-detail");

  await page.goto("/assessments");
  await page
    .locator("tbody tr")
    .first()
    .getByRole("button", { name: "Open" })
    .click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.screenshot({
    path: path.join(gallery, "07-assessment-detail.png"),
    fullPage: true,
  });

  const mobile = await browser.newContext({
    baseURL: "http://localhost:5173",
    viewport: { width: 390, height: 844 },
  });
  const mobilePage = await mobile.newPage();
  await mobilePage.goto("/");
  await mobilePage.locator("input[name=username]").fill("owner");
  await mobilePage.locator("input[name=password]").fill(password!);
  await mobilePage.locator("button.primary").click();
  await expect(
    mobilePage.getByRole("heading", { name: "مركز قيادة الحوكمة" }),
  ).toBeVisible();
  await mobilePage.screenshot({
    path: path.join(gallery, "23-mobile-dashboard-ar.png"),
    fullPage: true,
  });
  await mobile.close();
});
