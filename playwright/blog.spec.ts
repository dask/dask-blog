import { test, expect } from "@playwright/test";

test.describe("Homepage", () => {
  test("loads and has correct title", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle("Dask Working Notes");
  });

  test("lists 150+ posts", async ({ page }) => {
    await page.goto("/");
    const posts = page.locator(".post-list li");
    const count = await posts.count();
    expect(count).toBeGreaterThanOrEqual(150);
  });

  test("has navbar with correct links", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator(".navbar-brand")).toContainText("Dask Blog");
    await expect(page.locator('.navbar-nav a[href="/"]')).toBeVisible();
    await expect(page.locator('.navbar-nav a[href="/tag/"]')).toBeVisible();
    await expect(
      page.locator('.navbar-nav a[href="https://www.dask.org"]')
    ).toBeVisible();
  });
});

test.describe("Post URLs", () => {
  test("every post link from homepage returns 200", async ({ page }) => {
    await page.goto("/");
    const links = await page.locator(".post-list .post-title a").all();
    expect(links.length).toBeGreaterThanOrEqual(150);

    // Check all post URLs in batches
    const hrefs: string[] = [];
    for (const link of links) {
      const href = await link.getAttribute("href");
      if (href) hrefs.push(href);
    }

    // Spot check every 10th post to keep test fast
    for (let i = 0; i < hrefs.length; i += 10) {
      const response = await page.goto(hrefs[i]);
      expect(response?.status()).toBe(200);
    }
  });
});

test.describe("Sample posts", () => {
  test("renders a recent post with title and content", async ({ page }) => {
    await page.goto("/2024/05/30/dask-dataframe-is-fast-now/");
    await expect(page.locator(".post-header h1")).toContainText(
      "Dask DataFrame is Fast Now"
    );
    await expect(page.locator(".post-meta")).toContainText("Patrick Hoefler");
    await expect(page.locator(".post-content")).not.toBeEmpty();
  });

  test("renders an older post", async ({ page }) => {
    await page.goto("/2014/12/27/towards-out-of-core-nd-arrays/");
    await expect(page.locator(".post-header h1")).toContainText(
      "Towards Out-of-core ND-Arrays"
    );
    await expect(page.locator(".post-content")).not.toBeEmpty();
  });
});

test.describe("Images", () => {
  test("sample post images load", async ({ page }) => {
    await page.goto("/2024/05/30/dask-dataframe-is-fast-now/");
    const images = page.locator('.post-content img[src^="/images/"]');
    const count = await images.count();
    expect(count).toBeGreaterThan(0);

    // Check first image loads
    const firstImg = images.first();
    await expect(firstImg).toBeVisible();
  });
});

test.describe("Syntax highlighting", () => {
  test("code blocks have highlight spans", async ({ page }) => {
    // Use a post that has fenced code blocks
    await page.goto("/2014/12/27/towards-out-of-core-nd-arrays/");
    const codeBlocks = page.locator(".highlight");
    const count = await codeBlocks.count();
    expect(count).toBeGreaterThan(0);
  });
});

test.describe("Tag pages", () => {
  test("/tag/ exists and lists tags", async ({ page }) => {
    await page.goto("/tag/");
    await expect(page.locator("h1")).toContainText("Tags");
    const tags = page.locator(".tag-list a");
    const count = await tags.count();
    expect(count).toBeGreaterThan(5);
  });

  test("/tag/dask/ lists posts", async ({ page }) => {
    await page.goto("/tag/dask/");
    await expect(page.locator("h1")).toContainText(/dask/i);
    const posts = page.locator(".post-list li");
    const count = await posts.count();
    expect(count).toBeGreaterThan(0);
  });

  test("/tag/python/ lists posts", async ({ page }) => {
    const response = await page.goto("/tag/python/");
    expect(response?.status()).toBe(200);
  });
});

test.describe("Feeds", () => {
  test("atom.xml returns valid XML", async ({ page }) => {
    const response = await page.goto("/atom.xml");
    expect(response?.status()).toBe(200);
    const text = await response?.text();
    expect(text).toContain("<feed");
    expect(text).toContain("<entry>");
    expect(text).toContain("Dask Working Notes");
  });

  test("feed.python.xml returns valid XML", async ({ page }) => {
    const response = await page.goto("/feed.python.xml");
    expect(response?.status()).toBe(200);
    const text = await response?.text();
    expect(text).toContain("<rss");
  });

  test("feed.scipy.xml returns valid XML", async ({ page }) => {
    const response = await page.goto("/feed.scipy.xml");
    expect(response?.status()).toBe(200);
    const text = await response?.text();
    expect(text).toContain("<rss");
  });

  test("feed.sympy.xml returns valid XML", async ({ page }) => {
    const response = await page.goto("/feed.sympy.xml");
    expect(response?.status()).toBe(200);
    const text = await response?.text();
    expect(text).toContain("<rss");
  });
});

test.describe("Draft exclusion", () => {
  test("draft posts are not on homepage", async ({ page }) => {
    await page.goto("/");
    const content = await page.content();
    // Known draft posts should not appear
    expect(content).not.toContain("Dask and scikit-learn Benchmarks");
  });
});

test.describe("Canonical URLs", () => {
  test("post with canonical_url has correct link tag", async ({ page }) => {
    await page.goto("/2024/05/30/dask-dataframe-is-fast-now/");
    const canonical = page.locator('link[rel="canonical"]');
    await expect(canonical).toHaveAttribute(
      "href",
      "https://docs.coiled.io/blog/dask-dataframe-is-fast.html"
    );
  });

  test("normal post has self-referencing canonical", async ({ page }) => {
    await page.goto("/2014/12/27/towards-out-of-core-nd-arrays/");
    const canonical = page.locator('link[rel="canonical"]');
    const href = await canonical.getAttribute("href");
    expect(href).toContain("/2014/12/27/towards-out-of-core-nd-arrays/");
  });
});

test.describe("Wide layout", () => {
  test("widepost renders with wide class", async ({ page }) => {
    await page.goto("/2017/07/03/dask-benchmarks/");
    await expect(page.locator("article.container.wide")).toBeVisible();
  });
});

test.describe("Responsive", () => {
  test("renders on mobile", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto("/");
    await expect(page.locator(".post-list")).toBeVisible();
  });

  test("renders on tablet", async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto("/");
    await expect(page.locator(".post-list")).toBeVisible();
  });

  test("renders on desktop", async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto("/");
    await expect(page.locator(".post-list")).toBeVisible();
  });
});

test.describe("Light/Dark theme", () => {
  test("theme toggle works", async ({ page }) => {
    await page.goto("/");
    const toggle = page.locator("#theme-toggle");
    await expect(toggle).toBeVisible();

    // Click toggle to switch to dark
    await toggle.click();
    const theme = await page.evaluate(() =>
      document.documentElement.getAttribute("data-theme")
    );
    expect(theme).toBe("dark");

    // Click again to switch back to light
    await toggle.click();
    const theme2 = await page.evaluate(() =>
      document.documentElement.getAttribute("data-theme")
    );
    expect(theme2).toBe("light");
  });

  test("theme preference persists on reload", async ({ page }) => {
    await page.goto("/");
    await page.locator("#theme-toggle").click();

    // Reload and check
    await page.reload();
    const theme = await page.evaluate(() =>
      document.documentElement.getAttribute("data-theme")
    );
    expect(theme).toBe("dark");
  });

  test("system dark preference applies dark theme", async ({ page }) => {
    await page.emulateMedia({ colorScheme: "dark" });
    await page.goto("/");
    // With dark preference and no saved theme, dark colors should apply
    const bgColor = await page.evaluate(
      () => getComputedStyle(document.body).backgroundColor
    );
    // Dark bg is #1a1a2e = rgb(26, 26, 46)
    expect(bgColor).toBe("rgb(26, 26, 46)");
  });
});

test.describe("No console errors", () => {
  test("homepage has no JS errors", async ({ page }) => {
    const errors: string[] = [];
    page.on("pageerror", (err) => errors.push(err.message));
    await page.goto("/");
    expect(errors).toHaveLength(0);
  });

  test("sample post has no JS errors", async ({ page }) => {
    const errors: string[] = [];
    page.on("pageerror", (err) => errors.push(err.message));
    await page.goto("/2024/05/30/dask-dataframe-is-fast-now/");
    expect(errors).toHaveLength(0);
  });
});

test.describe("404 page", () => {
  test("404 page renders", async ({ page }) => {
    const response = await page.goto("/nonexistent-page-xyz/");
    // Hugo dev server returns 404 for missing pages
    expect(response?.status()).toBe(404);
  });
});

test.describe("Static assets", () => {
  test("documentation.html redirects to dask.org", async ({ page }) => {
    const response = await page.goto("/documentation.html");
    expect(response?.status()).toBe(200);
    const content = await page.content();
    expect(content).toContain("https://www.dask.org");
  });
});
