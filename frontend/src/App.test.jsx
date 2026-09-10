import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";

describe("URL shortener app", () => {
  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("creates a short URL and loads its analytics", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            short_code: "9IX",
            short_url: "http://localhost:8000/9IX",
          }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ total_clicks: 2, recent_clicks: [] }),
        }),
    );

    render(<App />);
    fireEvent.change(screen.getByLabelText("Long URL"), {
      target: { value: "https://example.com" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Shorten URL" }));

    expect(await screen.findByText("http://localhost:8000/9IX")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "View analytics" }));

    await waitFor(() => {
      expect(screen.getByText("2 total clicks")).toBeInTheDocument();
    });
  });

  it("shows API errors to the user", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        json: async () => ({ detail: "Invalid URL" }),
      }),
    );

    render(<App />);
    fireEvent.change(screen.getByLabelText("Long URL"), {
      target: { value: "https://example.com" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Shorten URL" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Invalid URL");
  });
});