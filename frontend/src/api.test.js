import { afterEach, describe, expect, it, vi } from "vitest";

import { getAnalytics, shortenUrl } from "./api";

describe("API client", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("posts a URL to the creation endpoint", async () => {
    const response = { ok: true, json: vi.fn().mockResolvedValue({ short_code: "9IX" }) };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response));

    await expect(shortenUrl("https://example.com")).resolves.toEqual({ short_code: "9IX" });
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/urls",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ url: "https://example.com" }),
      }),
    );
  });

  it("encodes short codes and surfaces API errors", async () => {
    const response = {
      ok: false,
      json: vi.fn().mockResolvedValue({ detail: "Short URL not found" }),
    };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response));

    await expect(getAnalytics("a/b")).rejects.toThrow("Short URL not found");
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/urls/a%2Fb/analytics",
      expect.any(Object),
    );
  });
});