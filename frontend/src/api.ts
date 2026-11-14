import { demoApi } from "./demo-api";

export const isDemoMode = import.meta.env.VITE_DEMO_MODE === "true";
export const publicAsset = (path: string) =>
  `${import.meta.env.BASE_URL}${path.replace(/^\//, "")}`;

export async function api<T = unknown>(
  path: string,
  method = "GET",
  data?: unknown,
): Promise<T> {
  if (isDemoMode) return demoApi<T>(path, method, data);
  const form = data instanceof FormData;
  const response = await fetch("/api" + path, {
    method,
    credentials: "same-origin",
    headers: {
      "X-Mizan-Request": "1",
      ...(!form && data ? { "Content-Type": "application/json" } : {}),
    },
    body: data ? (form ? data : JSON.stringify(data)) : undefined,
  });
  if (!response.ok) {
    const body = await response
      .json()
      .catch(() => ({ detail: "Request failed" }));
    throw new Error(
      typeof body.detail === "string"
        ? body.detail
        : JSON.stringify(body.detail),
    );
  }
  return response.json();
}
export type DomainRecord = {
  id: number;
  kind: string;
  title: string;
  department: string;
  version: number;
  payload: Record<string, unknown>;
};
export type Assessment = {
  id: number;
  control_id: number;
  asset_id: number;
  owner_id: number;
  reviewer_id: number | null;
  status: string;
  stage: string;
  rationale: string;
  period: string;
  version: number;
};
export type Finding = {
  id: number;
  assessment_id: number;
  risk_id: number;
  title: string;
  action: string;
  owner_id: number;
  due: string;
  state: string;
};
export type Evidence = {
  id: number;
  assessment_id: number;
  filename: string;
  sha256: string;
  created: string;
  review_due: string;
};
export type User = { id: number; username: string; role: string };
export type WorkItem = {
  id: number;
  uid: string;
  domain: string;
  record_type: string;
  title_ar: string;
  title_en: string;
  status: string;
  owner_id: number;
  owner: string;
  reviewer_id: number | null;
  reviewer: string | null;
  approver_id: number | null;
  approver: string | null;
  due_date: string | null;
  payload: Record<string, unknown>;
  simulated: boolean;
  simulation_label: string | null;
  version: number;
  updated_at: string;
  approvals: Record<string, unknown>[];
};
export type Dashboard = {
  compliance: {
    eligible: number;
    score: number | null;
    coverage: number | null;
    verified: number | null;
    evidence_coverage: number | null;
    method: string;
  };
  risks: number;
  critical_risks: number;
  high_risks: number;
  assets: number;
  open_findings: number;
  overdue: number;
  stale_evidence: number;
  open_gaps: number;
  overdue_remediation: number;
  control_status: Record<string, number>;
  policy_status: Record<string, number>;
  policy_acknowledgement: {
    acknowledged: number;
    assigned: number;
    rate: number | null;
  };
  vendor_risk_distribution: Record<string, number>;
  privacy_status: Record<string, number>;
  incident_status: Record<string, number>;
  treatment_progress: { closed: number; total: number };
  kpi_definitions: Record<string, string>;
  heatmap: {
    id: number;
    likelihood: number;
    impact: number;
    score: number;
    band: string;
  }[];
  timestamp: string;
};
