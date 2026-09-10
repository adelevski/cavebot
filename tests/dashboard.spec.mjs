import { test, expect } from "@playwright/test";
const tile = Buffer.from(
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAFgAI/ScLbtAAAAABJRU5ErkJggg==",
  "base64",
);

test.beforeEach(async ({ page }) => {
  await page.route("https://tile.openstreetmap.org/**", (route) =>
    route.fulfill({ contentType: "image/png", body: tile }),
  );
});

test("catalogue filters, comparison values and source links", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/");
  await expect(page).toHaveTitle("cave atlas");
  await expect(page.locator(".cave")).toHaveCount(45);
  await expect(page.locator("#results")).toBeHidden();
  await page.getByRole("searchbox").fill("Mexico");
  await expect(page.locator(".cave")).toHaveCount(4);
  await page
    .getByRole("button", { name: "Explore Chevé Cave", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Comparison", exact: true }),
  ).toBeVisible();
  await expect(page.locator(".metric-value")).toHaveText([
    "1,538 m",
    "96.1 km",
  ]);
  await expect(
    page.getByRole("link", { name: "Google: Chevé Cave" }),
  ).toHaveAttribute("href", /Chev%C3%A9/);
  await page.getByRole("button", { name: "Reset filters" }).click();
  for (const name of [
    "Krubera-Voronja Cave",
    "Hirlatzhöhle",
    "Veryovkina Cave",
  ]) {
    await page
      .getByRole("checkbox", { name: `Compare ${name}`, exact: true })
      .check();
  }
  await expect(page.locator(".result-card")).toHaveCount(4);
  const values = await page
    .locator(".bar")
    .evaluateAll((nodes) => nodes.map((n) => n.getBoundingClientRect().width));
  expect(values[0]).toBeLessThan(values[2]); // Chevé is shallower than Krubera.
  expect(values[1]).toBeGreaterThan(values[3]); // Chevé has longer surveyed passages.
  await page.locator("#region").selectOption("Spain");
  await expect(page.locator(".result-card")).toHaveCount(4);
  await page.getByRole("searchbox").fill("no such cave");
  await expect(page.locator(".empty")).toBeVisible();
  await page.getByRole("button", { name: "Close comparison" }).click();
  await page.locator("#results-toggle").click();
  await expect(page.locator(".result-card")).toHaveCount(4);
  await page.getByRole("button", { name: "Remove Chevé Cave" }).click();
  await expect(page.locator(".result-card")).toHaveCount(3);
  expect(errors).toEqual([]);
});

test("full catalogue selection scrolls without widening panels", async ({
  page,
}) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/");
  for (const checkbox of await page.getByRole("checkbox").all())
    await checkbox.check();
  await expect(page.locator(".result-card")).toHaveCount(45);
  expect(
    await page
      .locator(".results-body")
      .evaluate((n) => n.scrollHeight > n.clientHeight),
  ).toBe(true);
  expect(
    await page
      .locator("#results")
      .evaluate((n) => n.getBoundingClientRect().width),
  ).toBe(380);
  const origins = await page
    .locator(".metrics")
    .evaluateAll((nodes) => nodes.map((n) => n.getBoundingClientRect().left));
  expect(origins.every((x) => x === origins[0])).toBe(true);
  await page.locator("#clear").click();
  await expect(page.locator("#results")).toBeHidden();
});

test("mobile panels, units, keyboard dialog and narrow layout", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page
    .getByRole("button", { name: "Explore Krubera-Voronja Cave" })
    .click();
  await expect(page.locator("#controls")).toBeHidden();
  await expect(page.locator(".metric-value")).toHaveText(["2,224 m", "23 km"]);
  await page.locator("#browse-toggle").click();
  await page.getByRole("button", { name: "About the data" }).click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toBeHidden();
  await page.setViewportSize({ width: 320, height: 740 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.locator("#selection-open").click();
  expect(
    await page
      .locator(".metric-value")
      .evaluateAll((nodes) =>
        nodes.every((n) => n.scrollWidth <= n.clientWidth),
      ),
  ).toBe(true);
});

test("map library failure keeps list and comparisons available", async ({
  page,
}) => {
  await page.route("**/vendor/leaflet.js", (route) => route.abort());
  await page.goto("/");
  await expect(
    page.getByText("Map unavailable. Search and comparison remain available."),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Explore Krubera-Voronja Cave" })
    .click();
  await expect(page.locator(".metric-value")).toHaveText(["2,224 m", "23 km"]);
});
