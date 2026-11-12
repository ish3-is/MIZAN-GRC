import { describe, it, expect, vi, afterEach } from "vitest";
import { api } from "./api";
afterEach(() => vi.unstubAllGlobals());
describe("API trust boundary", () => {
  it("includes the CSRF header and same-origin credentials", async () => {
    const fetch = vi
      .fn()
      .mockResolvedValue({ ok: true, json: async () => ({ id: 1 }) });
    vi.stubGlobal("fetch", fetch);
    await api("/example", "POST", { state: "Draft" });
    expect(fetch.mock.calls[0][1].headers["X-Mizan-Request"]).toBe("1");
    expect(fetch.mock.calls[0][1].credentials).toBe("same-origin");
  });
  it("surfaces server rejection instead of reporting success", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue({
          ok: false,
          json: async () => ({ detail: "Independent reviewer required" }),
        }),
    );
    await expect(api("/review", "POST", {})).rejects.toThrow(
      "Independent reviewer required",
    );
  });
});
