import { test, expect } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
const env = fs.readFileSync(path.resolve("..", ".env"), "utf8");
const password = env.match(/^DEMO_PASSWORD=(.*)$/m)?.[1]?.trim();
test("Arabic dashboard, persisted assessment, independent review and responsive navigation", async ({
  page,
  browser,
}) => {
  test.skip(!password, "Run local bootstrap and start both services");
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/");
  await page.locator("input[name=username]").fill("owner");
  await page.locator("input[name=password]").fill(password!);
  await page.locator("button.primary").click();
  await expect(
    page.getByRole("heading", { name: "مركز قيادة الحوكمة" }),
  ).toBeVisible();
  await expect(page.locator("html")).toHaveAttribute("dir", "rtl");
  await expect(page.locator(".metric strong").nth(1)).toHaveText("40");
  await page.screenshot({
    path: "../docs/screenshots/dashboard-ar.png",
    fullPage: true,
  });
  await page.getByRole("button", { name: "English", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Governance Command Center" }),
  ).toBeVisible();
  await expect(page.locator("html")).toHaveAttribute("dir", "ltr");
  await page.screenshot({
    path: "../docs/screenshots/dashboard-en.png",
    fullPage: true,
  });
  await page.locator('nav a[href="/assessments"]').click();
  await page.getByRole("button", { name: "New assessment" }).click();
  const dialog = page.getByRole("dialog");
  await expect(dialog).toBeVisible();
  await dialog
    .locator("form")
    .first()
    .locator("select")
    .selectOption("Compliant");
  await dialog
    .locator("form")
    .first()
    .locator("textarea")
    .fill(
      "Browser test: synthetic approved access procedure and scoped sample inspected.",
    );
  await dialog
    .getByRole("button", { name: "Save assessment", exact: true })
    .click();
  await dialog
    .locator("input[type=file]")
    .setInputFiles({
      name: "synthetic-review.txt",
      mimeType: "text/plain",
      buffer: Buffer.from("SYNTHETIC reviewed and approved access sample"),
    });
  await dialog.locator("input[type=date]").fill("2027-12-31");
  await dialog.getByRole("button", { name: "Encrypt & attach" }).click();
  await expect(
    dialog.getByText("synthetic-review.txt", { exact: true }),
  ).toBeVisible();
  await dialog
    .getByRole("button", { name: "Submit for independent review" })
    .click();
  await expect(dialog.getByText("Submitted", { exact: true })).toBeVisible();
  await dialog.getByRole("button", { name: "Close", exact: true }).click();
  await page.reload();
  await expect(page.locator("tbody tr").last()).toContainText("Submitted");
  await page.screenshot({
    path: "../docs/screenshots/assessments-en.png",
    fullPage: true,
  });
  const reviewer = await browser.newContext({
    baseURL: "http://localhost:5173",
  });
  const p = await reviewer.newPage();
  await p.goto("/");
  await p.locator("input[name=username]").fill("auditor");
  await p.locator("input[name=password]").fill(password!);
  await p.locator("button.primary").click();
  await expect(
    p.getByRole("heading", { name: "مركز قيادة الحوكمة" }),
  ).toBeVisible();
  await p.getByRole("button", { name: "English", exact: true }).click();
  await p.locator('nav a[href="/assessments"]').click();
  await p
    .locator("tbody tr")
    .last()
    .getByRole("button", { name: "Open" })
    .click();
  await p
    .locator(".review-form textarea")
    .fill(
      "Independent browser retest: inspected synthetic sample, source and evidence validity.",
    );
  await p.getByRole("button", { name: "Record review" }).click();
  await expect(
    p.getByRole("dialog").getByText("Approved", { exact: true }),
  ).toBeVisible();
  await p.screenshot({
    path: "../docs/screenshots/review-en.png",
    fullPage: true,
  });
  await reviewer.close();
  await page.setViewportSize({ width: 390, height: 844 });
  await page.locator('nav a[href="/"]').click();
  await expect(
    page.getByRole("heading", { name: "Governance Command Center" }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.screenshot({
    path: "../docs/screenshots/mobile-en.png",
    fullPage: true,
  });
  expect(errors).toEqual([]);
});
