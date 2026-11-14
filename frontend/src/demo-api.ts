type DemoUser = { id: number; username: string; role: string };

type DemoPayload = {
  dashboard: unknown;
  users: DemoUser[];
  records: Record<string, unknown[]>;
  assessments: unknown[];
  evidence: unknown[];
  findings: unknown[];
  work_items: Array<{ domain: string; [key: string]: unknown }>;
  policy_acknowledgements: unknown[];
  relationships: unknown[];
  activity: unknown[];
  activity_verify: unknown;
  management_report: unknown;
};

let payloadPromise: Promise<DemoPayload> | null = null;

function loadPayload() {
  payloadPromise ??= fetch(`${import.meta.env.BASE_URL}demo-data.json`).then(
    async (response) => {
      if (!response.ok) throw new Error("Demo data could not be loaded");
      return response.json() as Promise<DemoPayload>;
    },
  );
  return payloadPromise;
}

function sessionUser(payload: DemoPayload) {
  const username = localStorage.getItem("mizan-pages-user");
  return payload.users.find((user) => user.username === username) || null;
}

export async function demoApi<T>(
  path: string,
  method = "GET",
  body?: unknown,
): Promise<T> {
  const payload = await loadPayload();
  const route = path.split("?")[0];
  const query = new URLSearchParams(path.split("?")[1] || "");

  if (route === "/login" && method === "POST") {
    const credentials = body as { username?: string; password?: string };
    const user = payload.users.find(
      (candidate) => candidate.username === credentials.username,
    );
    if (!user || credentials.password !== "demo") {
      throw new Error("Use a listed demo account with password: demo");
    }
    localStorage.setItem("mizan-pages-user", user.username);
    return user as T;
  }

  if (route === "/logout" && method === "POST") {
    localStorage.removeItem("mizan-pages-user");
    return { ok: true } as T;
  }

  const user = sessionUser(payload);
  if (!user) throw new Error("Sign in to the GitHub Pages showcase");

  if (method !== "GET") {
    throw new Error(
      "GitHub Pages is a read-only showcase. Run the full backend locally to save changes.",
    );
  }

  if (route === "/me") return user as T;
  if (route === "/users") return payload.users as T;
  if (route === "/dashboard") return payload.dashboard as T;
  if (route === "/assessments") return payload.assessments as T;
  if (route === "/evidence") return payload.evidence as T;
  if (route === "/findings") return payload.findings as T;
  if (route === "/policy-acknowledgements")
    return payload.policy_acknowledgements as T;
  if (route === "/relationships") return payload.relationships as T;
  if (route === "/activity/verify") return payload.activity_verify as T;
  if (route === "/activity") return payload.activity as T;
  if (route === "/reports/management") return payload.management_report as T;
  if (route === "/work-items") {
    const domain = query.get("domain");
    return payload.work_items.filter(
      (item) => !domain || item.domain === domain,
    ) as T;
  }
  if (route.startsWith("/records/")) {
    const kind = route.slice("/records/".length);
    return (payload.records[kind] || []) as T;
  }

  throw new Error(`The static showcase does not provide ${route}`);
}
