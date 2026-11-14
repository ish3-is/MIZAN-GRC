import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import {
  QueryClient,
  QueryClientProvider,
  useQuery,
} from "@tanstack/react-query";
import {
  BrowserRouter,
  HashRouter,
  NavLink,
  Route,
  Routes,
  useLocation,
} from "react-router-dom";
import {
  Activity,
  ArrowUpRight,
  Bell,
  BookOpen,
  BriefcaseBusiness,
  Building2,
  Check,
  ChevronLeft,
  ClipboardCheck,
  Download,
  FileCheck2,
  FileText,
  FolderLock,
  GraduationCap,
  Globe2,
  LayoutDashboard,
  LogOut,
  Moon,
  Sun,
  Plus,
  Scale,
  Search,
  Settings,
  Siren,
  ShieldCheck,
  ShieldAlert,
  Users,
  Workflow,
  X,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import {
  api,
  type DomainRecord,
  type Assessment,
  type Finding,
  type Evidence,
  type User,
  type Dashboard,
  type WorkItem,
  isDemoMode,
  publicAsset,
} from "./api";
import "./style.css";
import "./theme.css";

const qc = new QueryClient({
  defaultOptions: { queries: { retry: false, staleTime: 10000 } },
});
const useData = <T,>(path: string) =>
  useQuery({ queryKey: [path], queryFn: () => api<T>(path) });
const statuses = [
  "Not Assessed",
  "Not Applicable",
  "Compliant",
  "Partially Compliant",
  "Non-Compliant",
  "Pending Verification",
];
const text = (v: unknown) => (typeof v === "string" ? v : JSON.stringify(v));
const badge = (value: string) => (
  <span
    className={
      "badge " +
      (value === "Approved" || value === "Compliant" || value === "Closed"
        ? "good"
        : value === "Non-Compliant" ||
            value === "Open" ||
            value === "UNVERIFIED"
          ? "bad"
          : "")
    }
  >
    {value}
  </span>
);

function App() {
  const [theme, setTheme] = useState(() =>
    localStorage.getItem("mizan-theme") === "light" ? "light" : "dark",
  );
  React.useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("mizan-theme", theme);
    document
      .querySelector('meta[name="theme-color"]')
      ?.setAttribute("content", theme === "dark" ? "#0b1020" : "#f3f6f7");
  }, [theme]);
  const [lang, setLang] = useState(localStorage.getItem("mizan-lang") || "ar");
  const ar = lang === "ar";
  const t = (en: string, arabic: string) => (ar ? arabic : en);
  const themeToggle = (
    <button
      type="button"
      className="theme-toggle"
      aria-label={
        theme === "dark"
          ? t("Switch to light mode", "تفعيل الوضع الفاتح")
          : t("Switch to dark mode", "تفعيل الوضع الداكن")
      }
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      title={
        theme === "dark"
          ? t("Light mode", "الوضع الفاتح")
          : t("Dark mode", "الوضع الداكن")
      }
    >
      {theme === "dark" ? <Sun size={17} /> : <Moon size={17} />}
      <span>{theme === "dark" ? t("Light", "فاتح") : t("Dark", "داكن")}</span>
    </button>
  );
  const [user, setUser] = useState<User | null>(null);
  const [checked, setChecked] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [drawer, setDrawer] = useState<Assessment | null>(null);
  const location = useLocation();
  React.useEffect(() => {
    document.documentElement.dir = ar ? "rtl" : "ltr";
    document.documentElement.lang = lang;
    localStorage.setItem("mizan-lang", lang);
  }, [lang, ar]);
  React.useEffect(() => {
    api<User>("/me")
      .then(setUser)
      .catch(() => {})
      .finally(() => setChecked(true));
  }, []);
  async function act(fn: () => Promise<unknown>) {
    setError("");
    setBusy(true);
    try {
      await fn();
      await qc.invalidateQueries();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  const nav = [
    ["/", "Overview", "نظرة عامة", LayoutDashboard],
    ["/governance", "Governance", "مركز الحوكمة", Building2],
    ["/risks", "Risk register", "سجل المخاطر", ShieldAlert],
    ["/assessments", "Compliance", "مركز الامتثال", ClipboardCheck],
    ["/policies", "Policies", "مركز السياسات", BookOpen],
    ["/gaps", "Gaps", "تقييم الفجوات", ShieldAlert],
    ["/remediation", "Remediation", "المعالجة", Workflow],
    ["/evidence", "Evidence", "مستودع الأدلة", FileCheck2],
    ["/privacy", "Privacy / PDPL", "الخصوصية وحماية البيانات", FolderLock],
    ["/vendors", "Vendor risk", "مخاطر الموردين", BriefcaseBusiness],
    ["/incidents", "Incidents", "إدارة الحوادث", Siren],
    ["/continuity", "Continuity", "استمرارية الأعمال", Activity],
    ["/training", "Training", "التدريب والتوعية", GraduationCap],
    ["/sources", "Regulatory sources", "المصادر التنظيمية", Globe2],
    ["/audit", "Audit trail", "سجل التدقيق", Activity],
    ["/reports", "Reports", "التقارير", FileText],
    ["/settings", "Settings & roles", "الإعدادات والصلاحيات", Settings],
  ] as const;
  if (!checked)
    return (
      <div className="center">
        {t("Connecting to MIZAN…", "جارٍ الاتصال بميزان…")}
      </div>
    );
  if (!user)
    return (
      <div className="login">
        <section>
          <div className="brand">
            <Scale size={40} />
            <b>
              ميزان <small>MIZAN GRC</small>
            </b>
          </div>
          <span className="context-label">Governance with clarity</span>
          <h1>
            حوكمة واضحة.
            <br />
            قرارات موثوقة.
          </h1>
          <p>
            Governance, risk and privacy intelligence
            <br />
            for the Saudi enterprise.
          </p>
          <div className="login-note">
            <MadarCredit t={t} hero />
            بيئة تجريبية • بيانات اصطناعية فقط
            <br />
            Synthetic data · Local demonstration
            <br />
            <span>
              {t(
                "Project team: Mishal · Muath · Reemas · Aljory",
                "فريق المشروع: مشعل • معاذ • ريماس • الجوري",
              )}
            </span>
          </div>
        </section>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const f = new FormData(e.currentTarget);
            void act(async () => {
              const u = await api<User>(
                "/login",
                "POST",
                Object.fromEntries(f),
              );
              setUser(u);
            });
          }}
        >
          <div className="login-theme">{themeToggle}</div>
          <button
            type="button"
            className="language"
            onClick={() => setLang(ar ? "en" : "ar")}
          >
            العربية / English
          </button>
          <span className="context-label">MIZAN workspace</span>
          <h2>{t("Welcome back", "مرحباً بك في ميزان")}</h2>
          <p>
            {t(
              "Sign in with a locally provisioned demo account.",
              "سجّل الدخول بحساب تجريبي أُعدّ محلياً.",
            )}
          </p>
          <label>
            {t("Username", "اسم المستخدم")}
            <input
              name="username"
              autoComplete="username"
              required
              defaultValue={isDemoMode ? "admin" : "owner"}
            />
          </label>
          <label>
            {t("Password", "كلمة المرور")}
            <input
              name="password"
              type="password"
              autoComplete="current-password"
              required
              defaultValue={isDemoMode ? "demo" : undefined}
            />
          </label>
          {error && (
            <p role="alert" className="error">
              {error}
            </p>
          )}
          <button className="primary" disabled={busy}>
            {t("Sign in to workspace", "الدخول إلى مساحة العمل")}{" "}
            <ChevronLeft size={16} />
          </button>
          <p className="muted">
            {isDemoMode
              ? t(
                  "GitHub Pages showcase: use admin / demo. Changes are disabled; run the backend for persisted workflows.",
                  "عرض GitHub Pages: استخدم admin / demo. الحفظ معطل؛ شغّل الخادم للمسارات المحفوظة.",
                )
              : t(
                  "Use the password generated by local setup. Accounts include owner, analyst, auditor, manager, riskowner, privacy, executive and admin.",
                  "استخدم كلمة المرور التي أنشأها الإعداد المحلي. من الحسابات: owner، analyst، auditor، manager، riskowner، privacy، executive، admin.",
                )}
          </p>
        </form>
      </div>
    );
  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <Scale size={32} />
          <b>
            ميزان <small>MIZAN GRC</small>
          </b>
        </div>
        <div className="org">
          <span className="org-icon">م</span>
          <div>
            <strong>
              {t("Namaa Digital Solutions", "نماء للحلول الرقمية")}
            </strong>
            <small>{t("MIZAN DEMO", "بيئة ميزان التجريبية")}</small>
          </div>
        </div>
        <div className="nav-caption">{t("Workspace", "مساحة العمل")}</div>
        <nav>
          {nav.map(([path, en, arabic, Icon]) => (
            <NavLink
              key={path}
              end={path === "/"}
              to={path}
              aria-label={t(en, arabic)}
            >
              <Icon size={18} />
              <span>{t(en, arabic)}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <MadarCredit t={t} />
        </div>
      </aside>
      <div className="main">
        <header>
          <div className="breadcrumbs">
            {t("Workspace", "مساحة العمل")}
            <ChevronLeft size={14} />
            <strong>
              {t(
                nav.find((n) => n[0] === location.pathname)?.[1] || "Overview",
                nav.find((n) => n[0] === location.pathname)?.[2] || "نظرة عامة",
              )}
            </strong>
          </div>
          <div className="header-actions">
            {themeToggle}
            <button onClick={() => setLang(ar ? "en" : "ar")}>
              <Globe2 size={16} />
              {ar ? "English" : "العربية"}
            </button>
            <NavLink
              to="/remediation"
              aria-label={t("Open action queue", "فتح قائمة الإجراءات")}
            >
              <Bell size={19} />
            </NavLink>
            <div className="avatar">
              {user.username.slice(0, 1).toUpperCase()}
            </div>
            <div className="identity">
              <b>{user.username}</b>
              <small>{user.role}</small>
            </div>
            <button
              aria-label="Sign out"
              onClick={() =>
                void act(async () => {
                  await api("/logout", "POST");
                  setUser(null);
                  qc.clear();
                })
              }
            >
              <LogOut size={17} />
            </button>
          </div>
        </header>
        <main>
          <div className="demo-banner">
            <span className="live-dot" />
            {isDemoMode
              ? t(
                  "GITHUB PAGES SHOWCASE · Read-only synthetic data. Full persisted workflows require the backend.",
                  "عرض GITHUB PAGES • بيانات اصطناعية للقراءة فقط. المسارات المحفوظة تتطلب الخادم.",
                )
              : t(
                  "SYNTHETIC DEMONSTRATION · Selected controls only. Internal assessment does not constitute certification or regulatory approval.",
                  "بيئة اصطناعية • نطاق ضوابط مختار. التقييم الداخلي لا يُعدّ اعتماداً أو موافقة تنظيمية.",
                )}
          </div>
          {error && (
            <div role="alert" className="error">
              {error}
              <button onClick={() => setError("")}>
                <X size={16} />
              </button>
            </div>
          )}
          <Routes>
            <Route path="/" element={<Overview t={t} />} />
            <Route
              path="/assessments"
              element={
                <Assessments t={t} onOpen={setDrawer} act={act} user={user} />
              }
            />
            <Route
              path="/risks"
              element={<Risks t={t} act={act} user={user} />}
            />
            <Route
              path="/findings"
              element={<Findings t={t} act={act} user={user} />}
            />
            <Route path="/sources" element={<Sources t={t} />} />
            <Route
              path="/privacy"
              element={
                <OperationalCenter
                  domain="privacy"
                  title={t(
                    "Privacy / PDPL center",
                    "مركز الخصوصية وحماية البيانات",
                  )}
                  subtitle={t(
                    "Processing activities, legal-review flags, transfers and retention decisions.",
                    "أنشطة المعالجة وإشارات المراجعة القانونية وقرارات النقل والاحتفاظ.",
                  )}
                  t={t}
                  act={act}
                  user={user}
                />
              }
            />
            <Route
              path="/governance"
              element={
                <OperationalCenter
                  domain="governance"
                  title={t("Governance center", "مركز الحوكمة")}
                  subtitle={t(
                    "Charter, scope, RACI, decisions and management review with controlled approvals.",
                    "الميثاق والنطاق ومصفوفة المسؤوليات والقرارات ومراجعة الإدارة باعتمادات مضبوطة.",
                  )}
                  t={t}
                  act={act}
                  user={user}
                />
              }
            />
            <Route
              path="/policies"
              element={
                <OperationalCenter
                  domain="policy"
                  title={t("Policy center", "مركز السياسات")}
                  subtitle={t(
                    "Sixteen policies with procedures, tests, evidence expectations and lifecycle approvals.",
                    "ست عشرة سياسة مع إجراءات واختبارات ومتطلبات أدلة ودورة اعتماد.",
                  )}
                  t={t}
                  act={act}
                  user={user}
                />
              }
            />
            <Route
              path="/gaps"
              element={
                <OperationalCenter
                  domain="gap"
                  title={t("Gap assessment", "تقييم الفجوات")}
                  subtitle={t(
                    "Current state, expected state, risk priority and verification criteria.",
                    "الحالة الحالية والمتوقعة وأولوية المخاطر ومعايير التحقق.",
                  )}
                  t={t}
                  act={act}
                  user={user}
                />
              }
            />
            <Route
              path="/remediation"
              element={
                <OperationalCenter
                  domain="remediation"
                  title={t("Remediation center", "مركز المعالجة")}
                  subtitle={t(
                    "Actions cannot close without completion evidence and independent verification.",
                    "لا يغلق الإجراء دون دليل إكمال وتحقق مستقل.",
                  )}
                  t={t}
                  act={act}
                  user={user}
                />
              }
            />
            <Route
              path="/evidence"
              element={
                <OperationalCenter
                  domain="evidence"
                  title={t("Evidence repository", "مستودع الأدلة")}
                  subtitle={t(
                    "Synthetic metadata records plus encrypted file evidence attached to assessments.",
                    "سجلات وصفية اصطناعية مع أدلة ملفات مشفرة مرتبطة بالتقييمات.",
                  )}
                  t={t}
                  act={act}
                  user={user}
                />
              }
            />
            <Route
              path="/vendors"
              element={
                <OperationalCenter
                  domain="vendor"
                  title={t("Third-party risk", "مخاطر الأطراف الثالثة")}
                  subtitle={t(
                    "Due diligence, questionnaires, contractual review and periodic reassessment.",
                    "العناية الواجبة والاستبيانات والمراجعة التعاقدية وإعادة التقييم.",
                  )}
                  t={t}
                  act={act}
                  user={user}
                />
              }
            />
            <Route
              path="/incidents"
              element={
                <OperationalCenter
                  domain="incident"
                  title={t("Incident management", "إدارة الحوادث")}
                  subtitle={t(
                    "Fictional incidents linked to risks, controls, gaps and corrective actions.",
                    "حوادث افتراضية مرتبطة بالمخاطر والضوابط والفجوات والإجراءات التصحيحية.",
                  )}
                  t={t}
                  act={act}
                  user={user}
                />
              }
            />
            <Route
              path="/continuity"
              element={
                <OperationalCenter
                  domain="continuity"
                  title={t("Business continuity", "استمرارية الأعمال")}
                  subtitle={t(
                    "Critical services, recovery objectives, dependencies and exercise results.",
                    "الخدمات الحرجة وأهداف التعافي والاعتماديات ونتائج التمارين.",
                  )}
                  t={t}
                  act={act}
                  user={user}
                />
              }
            />
            <Route
              path="/training"
              element={
                <OperationalCenter
                  domain="training"
                  title={t("Training & awareness", "التدريب والتوعية")}
                  subtitle={t(
                    "Representative fictional completion and acknowledgement records.",
                    "سجلات إكمال وإقرار افتراضية بعينة ممثلة.",
                  )}
                  t={t}
                  act={act}
                  user={user}
                />
              }
            />
            <Route
              path="/acknowledgements"
              element={<Acknowledgements t={t} act={act} />}
            />
            <Route
              path="/data-inventory"
              element={
                <Registry
                  t={t}
                  title={t("Data and asset inventory", "جرد البيانات والأصول")}
                  subtitle={t(
                    "Fictional assets only; no real personal data.",
                    "أصول افتراضية فقط؛ لا توجد بيانات شخصية حقيقية.",
                  )}
                  kinds={["asset", "employee"]}
                />
              }
            />
            <Route
              path="/settings"
              element={<SettingsAndRoles t={t} act={act} user={user} />}
            />
            <Route path="/audit" element={<Audit t={t} act={act} />} />
            <Route path="/reports" element={<Reports t={t} act={act} />} />
            <Route
              path="*"
              element={<p>Page not found / الصفحة غير موجودة</p>}
            />
          </Routes>
          <footer>
            <div className="footer-credit">
              {t(
                "MIZAN — A project by MaDar Academy",
                "ميزان — أحد أعمال منظومة مدار التقنية",
              )}
              <small>MaDar Academy · MIZAN GRC © 2026</small>
              <small>
                {t(
                  "Mishal · Muath · Reemas · Aljory",
                  "مشعل • معاذ • ريماس • الجوري",
                )}
              </small>
            </div>
            {t(
              "MIZAN supports compliance management. It does not provide legal advice, certification or regulatory approval.",
              "ميزان يدعم إدارة الامتثال، ولا يقدم مشورة قانونية أو شهادة اعتماد أو موافقة تنظيمية.",
            )}
          </footer>
        </main>
      </div>
      {drawer && (
        <AssessmentDrawer
          a={drawer}
          close={() => setDrawer(null)}
          t={t}
          act={act}
          user={user}
          busy={busy}
        />
      )}
    </div>
  );
}
type T = (en: string, ar: string) => string;
function MadarCredit({ t, hero = false }: { t: T; hero?: boolean }) {
  return (
    <div className={`madar-credit${hero ? " madar-credit-hero" : ""}`}>
      <img
        src={publicAsset("brand/madar-academy.png")}
        alt={t("MaDar Academy logo", "شعار منظومة مدار التقنية")}
        width={hero ? 94 : 46}
        height={hero ? 94 : 46}
      />
      <div>
        <span className="credit-label">{t("A project by", "أحد أعمال")}</span>
        <strong>{t("MaDar Academy", "منظومة مدار التقنية")}</strong>
        <small>
          {t("Knowledge. Engineering. Impact.", "معرفة. هندسة. أثر.")}
        </small>
      </div>
    </div>
  );
}
type Act = (fn: () => Promise<unknown>) => Promise<void>;
function Title({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children?: React.ReactNode;
}) {
  return (
    <div className="page-title">
      <div>
        <span className="context-label">MIZAN intelligence</span>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
      <div>{children}</div>
    </div>
  );
}
function Loading({ error }: { error?: Error | null }) {
  return (
    <div className="panel empty" role={error ? "alert" : "status"}>
      {error ? error.message : "Loading / جارٍ التحميل…"}
    </div>
  );
}
function Overview({ t }: { t: T }) {
  const q = useData<Dashboard>("/dashboard");
  const actions = useData<WorkItem[]>("/work-items?domain=remediation");
  const controls = useData<DomainRecord[]>("/records/control");
  if (!q.data) return <Loading error={q.error} />;
  const d = q.data;
  const cards = [
    [
      t("Registered risks", "المخاطر المسجلة"),
      d.risks,
      t(
        `${d.critical_risks} critical · ${d.high_risks} high`,
        `${d.critical_risks} حرجة • ${d.high_risks} مرتفعة`,
      ),
    ],
    [
      t("Open gaps", "الفجوات المفتوحة"),
      d.open_gaps,
      t("Risk-prioritized control weaknesses", "نقاط ضعف مرتبة حسب المخاطر"),
    ],
    [
      t("Overdue remediation", "المعالجات المتأخرة"),
      d.overdue_remediation,
      t("Due before the reporting date", "مستحقة قبل تاريخ التقرير"),
    ],
    [
      t("Policy acknowledgement", "إقرار السياسات"),
      d.policy_acknowledgement.rate === null
        ? "—"
        : `${d.policy_acknowledgement.rate}%`,
      t(
        `${d.policy_acknowledgement.acknowledged} of ${d.policy_acknowledgement.assigned} sample assignments`,
        `${d.policy_acknowledgement.acknowledged} من ${d.policy_acknowledgement.assigned} تكليفات في العينة`,
      ),
    ],
  ] as const;
  const distribution = ["Low", "Moderate", "High", "Critical"].map((b) => ({
    name: b,
    count: d.heatmap.filter((r) => r.band === b).length,
  }));
  return (
    <>
      <Title
        title={t("Governance Command Center", "مركز قيادة الحوكمة")}
        subtitle={t(
          "A clear view of your controls, risks and next decisions.",
          "رؤية متكاملة للضوابط والمخاطر والقرارات القادمة.",
        )}
      >
        <NavLink className="primary" to="/reports">
          <Download size={16} />
          {t("Management report", "تقرير الإدارة")}
        </NavLink>
      </Title>
      <div className="scope">
        <span>
          <span className="live-dot" />
          {t("Current scope", "النطاق الحالي")}
        </span>
        <b>NCA ECC 2:2024</b>
        <span>2026-Q4</span>
        <span>
          {t(
            "Namaa Digital Solutions · 8 departments",
            "نماء للحلول الرقمية • ٨ إدارات",
          )}
        </span>
        <small>{t("Selected starter controls", "ضوابط بداية مختارة")}</small>
      </div>
      <div className="metrics">
        {cards.map(([label, value, note]) => (
          <article className="metric" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
            <small>{note}</small>
          </article>
        ))}
      </div>
      <div className="dashboard-grid">
        <section className="panel">
          <div className="panel-heading">
            <div>
              <h2>{t("Assessment assurance", "مستوى ضمان التقييم")}</h2>
              <p>
                {t(
                  "Coverage and verification are reported separately",
                  "فصل تغطية التقييم عن التحقق المستقل",
                )}
              </p>
            </div>
            <NavLink to="/assessments">
              <ArrowUpRight size={18} />
            </NavLink>
          </div>
          <div className="assurance">
            <div
              className="ring"
              style={
                {
                  "--progress": `${(d.compliance.verified || 0) * 3.6}deg`,
                } as React.CSSProperties
              }
            >
              <div>
                <b>{d.compliance.verified ?? "—"}%</b>
                <small>{t("independently approved", "اعتماد مستقل")}</small>
              </div>
            </div>
            <div className="progress-list">
              {[
                [
                  t("Assessment coverage", "تغطية التقييم"),
                  d.compliance.coverage,
                ],
                [
                  t("Evidence coverage", "تغطية الأدلة"),
                  d.compliance.evidence_coverage,
                ],
                [
                  t("Independent approval", "الاعتماد المستقل"),
                  d.compliance.verified,
                ],
              ].map(([label, value]) => (
                <div key={String(label)}>
                  <div>
                    <span>{label}</span>
                    <b>{value ?? "—"}%</b>
                  </div>
                  <progress max={100} value={Number(value || 0)} />
                </div>
              ))}
            </div>
          </div>
          <div className="panel-note">
            {t(
              "Unassessed items receive no credit. Only approved, justified N/A items are excluded.",
              "العناصر غير المقيّمة لا تحصل على رصيد. يُستبعد غير المنطبق بعد التبرير والاعتماد فقط.",
            )}
          </div>
        </section>
        <section className="panel">
          <div className="panel-heading">
            <div>
              <h2>{t("Residual risk heatmap", "خريطة المخاطر المتبقية")}</h2>
              <p>
                {t(
                  "Likelihood × impact · ordinal prioritization",
                  "الاحتمالية × الأثر • ترتيب الأولوية",
                )}
              </p>
            </div>
            <span className="badge">5 × 5</span>
          </div>
          <div className="heatmap-wrap">
            <span className="axis-label">{t("Likelihood", "الاحتمالية")}</span>
            <div className="heatmap">
              {[5, 4, 3, 2, 1].flatMap((l) =>
                [1, 2, 3, 4, 5].map((i) => {
                  const count = d.heatmap.filter(
                    (r) => r.likelihood === l && r.impact === i,
                  ).length;
                  return (
                    <div
                      tabIndex={0}
                      title={`${l} × ${i}: ${count}`}
                      key={`${l}-${i}`}
                      className={
                        "cell " +
                        (l * i >= 17
                          ? "critical"
                          : l * i >= 10
                            ? "high"
                            : l * i >= 5
                              ? "moderate"
                              : "low")
                      }
                    >
                      {count || "·"}
                    </div>
                  );
                }),
              )}
            </div>
          </div>
          <div className="heatmap-caption">
            1 ← {t("Impact", "الأثر")} → 5{" "}
            <span>
              {t(
                "Risk appetite: 9 (organizational)",
                "شهية المخاطر: ٩ (معيار داخلي)",
              )}
            </span>
          </div>
        </section>
        <section className="panel wide">
          <div className="panel-heading">
            <div>
              <h2>
                {t("Decisions requiring attention", "قرارات تستدعي الانتباه")}
              </h2>
              <p>
                {t(
                  "Accountability starts with a clear next action",
                  "تبدأ المساءلة بإجراء تالٍ واضح",
                )}
              </p>
            </div>
            <NavLink to="/findings">
              {t("View actions", "عرض الإجراءات")} <ChevronLeft size={15} />
            </NavLink>
          </div>
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>{t("Finding", "الفجوة")}</th>
                  <th>{t("Action", "الإجراء")}</th>
                  <th>{t("Due date", "تاريخ الاستحقاق")}</th>
                  <th>{t("State", "الحالة")}</th>
                </tr>
              </thead>
              <tbody>
                {actions.data
                  ?.filter((f) => f.status !== "Closed")
                  .slice(0, 5)
                  .map((f) => (
                    <tr key={f.id}>
                      <td>
                        <b>{t(f.title_en, f.title_ar)}</b>
                        <small>{f.uid}</small>
                      </td>
                      <td>{String(f.payload.plan || "—")}</td>
                      <td dir="ltr">{f.due_date || "—"}</td>
                      <td>{badge(f.status)}</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
          {!actions.data?.length && (
            <p className="empty">
              {t("No findings recorded", "لا توجد فجوات مسجلة")}
            </p>
          )}
        </section>
        <section className="panel">
          <div className="panel-heading">
            <h2>{t("Risk exposure distribution", "توزيع التعرض للمخاطر")}</h2>
          </div>
          <ResponsiveContainer width="100%" height={190}>
            <BarChart data={distribution}>
              <XAxis
                dataKey="name"
                tick={{ fontSize: 12, fill: "var(--chart-tick, #72848e)" }}
              />
              <YAxis
                allowDecimals={false}
                tick={{ fill: "var(--chart-tick, #72848e)" }}
              />
              <Tooltip />
              <Bar
                dataKey="count"
                fill="#247f7c"
                radius={[5, 5, 0, 0]}
                isAnimationActive={false}
              />
            </BarChart>
          </ResponsiveContainer>
        </section>
        <section className="panel">
          <div className="panel-heading">
            <h2>{t("Regulatory scope", "النطاق التنظيمي")}</h2>
            <Globe2 size={18} />
          </div>
          <div className="scope-info">
            <b>NCA ECC 2:2024</b>
            <p>
              {t(
                `${controls.data?.length || 0} selected references checked; applicability review pending.`,
                `${controls.data?.length || 0} مراجع مختارة تم فحصها؛ مراجعة الانطباق قيد الانتظار.`,
              )}
            </p>
            <NavLink to="/sources">
              {t("Inspect provenance", "فحص المصدر والتوثيق")}{" "}
              <ArrowUpRight size={15} />
            </NavLink>
            <div className="warning">
              {t(
                "PDPL article mappings and statutory timers are not activated until authoritative review.",
                "لم تُفعّل ربط مواد نظام حماية البيانات أو المهل النظامية لحين المراجعة الموثوقة.",
              )}
            </div>
          </div>
        </section>
      </div>
    </>
  );
}
function Assessments({
  t,
  onOpen,
  act,
  user,
}: {
  t: T;
  onOpen: (a: Assessment) => void;
  act: Act;
  user: User;
}) {
  const aa = useData<Assessment[]>("/assessments");
  const cc = useData<DomainRecord[]>("/records/control");
  const assets = useData<DomainRecord[]>("/records/asset");
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  return (
    <>
      <Title
        title={t("Compliance assessments", "تقييمات الامتثال")}
        subtitle={t(
          "Owner assessment → evidence → independent review → approval",
          "تقييم المالك ← الأدلة ← المراجعة المستقلة ← الاعتماد",
        )}
      />
      {["owner", "compliance", "manager", "admin"].includes(user.username) && (
        <form
          className="inline-form panel"
          onSubmit={(e) => {
            e.preventDefault();
            const f = new FormData(e.currentTarget);
            void act(async () => {
              const a = await api<Assessment>("/assessments", "POST", {
                control_id: Number(f.get("control")),
                asset_id: Number(f.get("asset")),
              });
              onOpen(a);
            });
          }}
        >
          <select name="control" aria-label="Control">
            {cc.data?.map((c) => (
              <option key={c.id} value={c.id}>
                {String(c.payload.exact_reference_id)} · {c.title}
              </option>
            ))}
          </select>
          <select name="asset" aria-label="Asset">
            {assets.data?.map((a) => (
              <option key={a.id} value={a.id}>
                {a.title}
              </option>
            ))}
          </select>
          <button className="primary">
            <Plus size={16} />
            {t("New assessment", "تقييم جديد")}
          </button>
        </form>
      )}
      <div className="panel">
        <div className="toolbar">
          <label className="search">
            <Search size={17} />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={t("Search controls…", "البحث في الضوابط…")}
            />
          </label>
          <select
            aria-label="Filter status"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            <option value="">{t("All statuses", "جميع الحالات")}</option>
            {statuses.map((s) => (
              <option key={s}>{s}</option>
            ))}
          </select>
        </div>
        {aa.isLoading ? (
          <Loading />
        ) : aa.error ? (
          <Loading error={aa.error} />
        ) : (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  {[
                    "ID",
                    "Control / الضابط",
                    "Asset / الأصل",
                    "Status / الحالة",
                    "Review / المراجعة",
                    "",
                  ].map((v) => (
                    <th key={v}>{v}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {aa.data
                  ?.filter(
                    (a) =>
                      (!status || a.status === status) &&
                      (cc.data?.find((c) => c.id === a.control_id)?.title || "")
                        .toLowerCase()
                        .includes(search.toLowerCase()),
                  )
                  .map((a) => (
                    <tr key={a.id}>
                      <td>ASM-{a.id}</td>
                      <td>
                        <b>
                          {cc.data?.find((c) => c.id === a.control_id)?.title}
                        </b>
                        <small>
                          {String(
                            cc.data?.find((c) => c.id === a.control_id)?.payload
                              .exact_reference_id || "",
                          )}
                        </small>
                      </td>
                      <td>
                        {assets.data?.find((v) => v.id === a.asset_id)?.title}
                      </td>
                      <td>{badge(a.status)}</td>
                      <td>{badge(a.stage)}</td>
                      <td>
                        <button
                          className="text-button"
                          onClick={() => onOpen(a)}
                        >
                          {t("Open", "فتح")} <ArrowUpRight size={15} />
                        </button>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
}
function AssessmentDrawer({
  a,
  close,
  t,
  act,
  user,
  busy,
}: {
  a: Assessment;
  close: () => void;
  t: T;
  act: Act;
  user: User;
  busy: boolean;
}) {
  const q = useData<Assessment[]>("/assessments");
  const current = q.data?.find((v) => v.id === a.id) || a;
  const cc = useData<DomainRecord[]>("/records/control");
  const ee = useData<Evidence[]>("/evidence");
  const control = cc.data?.find((c) => c.id === current.control_id);
  const [status, setStatus] = useState(current.status);
  const [rationale, setRationale] = useState(current.rationale);
  const drawerRef = React.useRef<HTMLElement>(null);
  React.useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = originalOverflow;
      previous?.focus();
    };
  }, []);
  const editable =
    current.owner_id === user.id &&
    ["Draft", "Returned"].includes(current.stage);
  return (
    <div className="overlay" onClick={close}>
      <section
        ref={drawerRef}
        className="drawer"
        role="dialog"
        aria-modal="true"
        aria-label="Assessment details"
        onClick={(e) => e.stopPropagation()}
        onKeyDown={(e) => {
          if (e.key === "Escape") close();
          if (e.key === "Tab") {
            const targets = Array.from(
              drawerRef.current?.querySelectorAll<HTMLElement>(
                "button:not([disabled]), a[href], input:not([disabled]), textarea:not([disabled]), select:not([disabled])",
              ) || [],
            );
            const first = targets[0],
              last = targets[targets.length - 1];
            if (e.shiftKey && document.activeElement === first) {
              e.preventDefault();
              last?.focus();
            } else if (!e.shiftKey && document.activeElement === last) {
              e.preventDefault();
              first?.focus();
            }
          }
        }}
      >
        <div className="drawer-head">
          <span className="context-label">ASSESSMENT · ASM-{a.id}</span>
          <button autoFocus onClick={close} aria-label="Close">
            <X />
          </button>
        </div>
        <h2>{control?.title}</h2>
        <div className="inline-badges">
          {badge(current.status)}
          {badge(current.stage)}
          <span>v{current.version}</span>
        </div>
        <div className="source-card">
          <b>
            {String(control?.payload.exact_reference_id || "")} · ECC 2:2024
          </b>
          <p>{String(control?.payload.requirement_summary || "")}</p>
          <small>{String(control?.payload.verification_status || "")}</small>
          <a
            href={String(control?.payload.official_source_url || "#")}
            target="_blank"
            rel="noreferrer"
          >
            {t("Official source", "المصدر الرسمي")} ↗
          </a>
        </div>
        <h3>{t("Assessment rationale", "مبررات التقييم")}</h3>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            void act(() =>
              api("/assessments/" + a.id, "PUT", {
                status,
                rationale,
                version: current.version,
              }),
            );
          }}
        >
          <label>
            {t("Status", "الحالة")}
            <select
              value={status}
              disabled={!editable}
              onChange={(e) => setStatus(e.target.value)}
            >
              {statuses.map((s) => (
                <option key={s}>{s}</option>
              ))}
            </select>
          </label>
          <label>
            {t("Rationale and sampling limits", "المبررات وحدود العينة")}
            <textarea
              minLength={10}
              maxLength={4000}
              required
              value={rationale}
              disabled={!editable}
              onChange={(e) => setRationale(e.target.value)}
            />
          </label>
          {editable && (
            <button disabled={busy} className="primary">
              {t("Save assessment", "حفظ التقييم")}
            </button>
          )}
        </form>
        <h3>{t("Evidence register", "سجل الأدلة")}</h3>
        {ee.data
          ?.filter((e) => e.assessment_id === a.id)
          .map((e) => (
            <div key={e.id} className="evidence-item">
              <FileCheck2 size={18} />
              <div>
                <b>{e.filename}</b>
                <small>
                  {t("Review due", "المراجعة مستحقة")}: {e.review_due}
                </small>
                <code title={e.sha256}>SHA-256 {e.sha256.slice(0, 18)}…</code>
              </div>
              <a
                href={
                  isDemoMode
                    ? publicAsset("downloads/synthetic-evidence.txt")
                    : "/api/evidence/" + e.id + "/download"
                }
                aria-label="Download evidence"
              >
                <Download size={16} />
              </a>
            </div>
          ))}
        {!ee.data?.some((e) => e.assessment_id === a.id) && (
          <div className="empty">
            {t("No evidence attached", "لم تُرفق أدلة")}
          </div>
        )}
        {editable && (
          <form
            className="upload-form"
            onSubmit={(e) => {
              e.preventDefault();
              const f = new FormData(e.currentTarget);
              void act(() =>
                api("/assessments/" + a.id + "/evidence", "POST", f),
              );
            }}
          >
            <label>
              {t(
                "Attach synthetic evidence (≤5 MB)",
                "إرفاق دليل اصطناعي (٥ م.ب كحد أقصى)",
              )}
              <input
                type="file"
                name="file"
                accept=".txt,.csv,.pdf,.png"
                required
              />
            </label>
            <label>
              {t("Organizational review date", "تاريخ المراجعة الداخلي")}
              <input type="date" name="review_due" required />
            </label>
            <button disabled={busy}>
              {t("Encrypt & attach", "تشفير وإرفاق")}
            </button>
          </form>
        )}
        <div className="workflow-actions">
          {editable && (
            <button
              className="primary"
              disabled={busy}
              onClick={() =>
                void act(() => api("/assessments/" + a.id + "/submit", "POST"))
              }
            >
              {t("Submit for independent review", "إرسال للمراجعة المستقلة")}
            </button>
          )}
          {current.stage === "Approved" && current.owner_id === user.id && (
            <button
              onClick={() =>
                void act(() => api("/assessments/" + a.id + "/reopen", "POST"))
              }
            >
              {t("Start reassessment", "بدء إعادة التقييم")}
            </button>
          )}
        </div>
        {["GRC Manager", "Internal Auditor"].includes(user.role) &&
          current.stage === "Submitted" && (
            <form
              className="review-form"
              onSubmit={(e) => {
                e.preventDefault();
                const f = new FormData(e.currentTarget);
                void act(() =>
                  api(
                    "/assessments/" + a.id + "/review",
                    "POST",
                    Object.fromEntries(f),
                  ),
                );
              }}
            >
              <h3>{t("Independent verification", "التحقق المستقل")}</h3>
              <p>
                {t(
                  "Inspect evidence content, scope, validity and sampling. Self-approval is blocked by the API.",
                  "افحص محتوى الأدلة ونطاقها وصلاحيتها والعينة. تمنع الواجهة البرمجية اعتماد الشخص لتقييمه.",
                )}
              </p>
              <select name="decision">
                <option value="approve">Approve / اعتماد</option>
                <option value="return">Return / إعادة</option>
              </select>
              <textarea
                name="rationale"
                required
                minLength={10}
                placeholder="Reviewer rationale / مبررات المراجع"
              />
              <button className="primary" disabled={busy}>
                {t("Record review", "تسجيل المراجعة")}
              </button>
            </form>
          )}
      </section>
    </div>
  );
}
function Risks({ t, act, user }: { t: T; act: Act; user: User }) {
  const rr = useData<DomainRecord[]>("/records/risk");
  const assets = useData<DomainRecord[]>("/records/asset");
  const [query, setQuery] = useState("");
  const [show, setShow] = useState(false);
  return (
    <>
      <Title
        title={t("Enterprise risk register", "سجل مخاطر المنشأة")}
        subtitle={t(
          "Independent inherent and residual ratings. No implied statistical precision.",
          "تقديرات مستقلة للمخاطر الكامنة والمتبقية دون ادعاء دقة إحصائية.",
        )}
      >
        <button className="primary" onClick={() => setShow(!show)}>
          <Plus size={16} />
          {t("Evaluate a risk", "تقييم خطر")}
        </button>
      </Title>
      {show && (
        <form
          className="panel form-grid"
          onSubmit={(e) => {
            e.preventDefault();
            const f = Object.fromEntries(new FormData(e.currentTarget));
            const data = {
              ...f,
              asset_id: Number(f.asset_id),
              ...Object.fromEntries(
                [
                  "inherent_likelihood",
                  "inherent_impact",
                  "residual_likelihood",
                  "residual_impact",
                ].map((k) => [k, Number(f[k])]),
              ),
            };
            void act(async () => {
              await api("/risks", "POST", data);
              setShow(false);
            });
          }}
        >
          <label>
            Title / العنوان
            <input name="title" minLength={5} required />
          </label>
          <label>
            Department / الإدارة
            <select name="department">
              {[
                "Technology",
                "Human Resources",
                "Finance",
                "Operations",
                "Governance",
              ].map((d) => (
                <option key={d}>{d}</option>
              ))}
            </select>
          </label>
          <label>
            Asset / الأصل
            <select name="asset_id">
              {assets.data?.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.title}
                </option>
              ))}
            </select>
          </label>
          <label>
            Treatment / المعالجة
            <select name="treatment">
              {["mitigate", "avoid", "transfer", "accept"].map((v) => (
                <option key={v}>{v}</option>
              ))}
            </select>
          </label>
          {[
            "inherent_likelihood",
            "inherent_impact",
            "residual_likelihood",
            "residual_impact",
          ].map((k) => (
            <label key={k}>
              {k.replaceAll("_", " ")}
              <input
                name={k}
                type="number"
                min={1}
                max={5}
                required
                defaultValue={3}
              />
            </label>
          ))}
          {[
            "inherent_rationale",
            "control_effectiveness_rationale",
            "residual_rationale",
          ].map((k) => (
            <label key={k}>
              {k.replaceAll("_", " ")}
              <textarea name={k} minLength={10} maxLength={2000} required />
            </label>
          ))}
          <button className="primary">
            {t("Save evaluation", "حفظ التقييم")}
          </button>
        </form>
      )}
      <div className="panel">
        <div className="toolbar">
          <label className="search">
            <Search size={17} />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={t(
                "Search risk or department",
                "البحث بالخطر أو الإدارة",
              )}
            />
          </label>
          <a
            className="button"
            href={
              isDemoMode
                ? publicAsset("downloads/mizan-demo-risks.csv")
                : "/api/reports/risks.csv"
            }
          >
            <Download size={16} /> CSV
          </a>
        </div>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                {[
                  "Risk / الخطر",
                  "Department / الإدارة",
                  "Inherent / كامن",
                  "Residual / متبقٍ",
                  "Treatment / المعالجة",
                ].map((s) => (
                  <th key={s}>{s}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rr.data
                ?.filter((r) =>
                  (r.title + r.department)
                    .toLowerCase()
                    .includes(query.toLowerCase()),
                )
                .map((r) => (
                  <tr key={r.id}>
                    <td>
                      <details>
                        <summary>
                          <b>{r.title}</b>
                        </summary>
                        <p>{String(r.payload.inherent_rationale)}</p>
                        <p>
                          {String(r.payload.control_effectiveness_rationale)}
                        </p>
                        <p>{String(r.payload.residual_rationale)}</p>
                        <small>{String(r.payload.assessed_at)}</small>
                      </details>
                    </td>
                    <td>{r.department}</td>
                    <td>
                      <span className="risk-number">
                        {Number(r.payload.inherent_likelihood) *
                          Number(r.payload.inherent_impact)}
                      </span>
                    </td>
                    <td>
                      <span className="risk-number teal">
                        {Number(r.payload.residual_likelihood) *
                          Number(r.payload.residual_impact)}
                      </span>
                    </td>
                    <td>
                      {String(r.payload.treatment)}
                      {Boolean(r.payload.acceptance) &&
                        badge(String(r.payload.acceptance))}
                      {user.role === "GRC Manager" &&
                        r.payload.acceptance === "Pending" && (
                          <form
                            onSubmit={(e) => {
                              e.preventDefault();
                              const f = new FormData(e.currentTarget);
                              void act(() =>
                                api(
                                  "/risks/" + r.id + "/accept",
                                  "POST",
                                  Object.fromEntries(f),
                                ),
                              );
                            }}
                          >
                            <input
                              name="rationale"
                              required
                              minLength={10}
                              placeholder="Acceptance rationale"
                            />
                            <input name="review_date" type="date" required />
                            <button>Approve acceptance</button>
                          </form>
                        )}
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
        {rr.error && <Loading error={rr.error} />}
      </div>
    </>
  );
}
function Findings({ t, act, user }: { t: T; act: Act; user: User }) {
  const q = useData<Finding[]>("/findings");
  const aa = useData<Assessment[]>("/assessments");
  const rr = useData<DomainRecord[]>("/records/risk");
  const users = useData<User[]>("/users");
  const [show, setShow] = useState(false);
  return (
    <>
      <Title
        title={t("Remediation workspace", "مساحة المعالجة")}
        subtitle={t(
          "Every gap links a control assessment to risk, accountability and retest.",
          "تربط كل فجوة تقييم الضابط بالخطر والمسؤولية وإعادة الاختبار.",
        )}
      >
        <button className="primary" onClick={() => setShow(!show)}>
          <Plus size={16} />
          {t("Register a gap", "تسجيل فجوة")}
        </button>
      </Title>
      {show && (
        <form
          className="panel form-grid"
          onSubmit={(e) => {
            e.preventDefault();
            const f = Object.fromEntries(new FormData(e.currentTarget));
            void act(async () => {
              await api("/findings", "POST", {
                ...f,
                assessment_id: Number(f.assessment_id),
                risk_id: Number(f.risk_id),
                owner_id: Number(f.owner_id),
              });
              setShow(false);
            });
          }}
        >
          <label>
            Finding title / عنوان الفجوة
            <input name="title" minLength={5} required />
          </label>
          <label>
            Corrective action / الإجراء
            <textarea name="action" required minLength={10} />
          </label>
          <label>
            Assessment / التقييم
            <select name="assessment_id">
              {aa.data?.map((a) => (
                <option key={a.id} value={a.id}>
                  ASM-{a.id}
                </option>
              ))}
            </select>
          </label>
          <label>
            Risk / الخطر
            <select name="risk_id">
              {rr.data?.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.title}
                </option>
              ))}
            </select>
          </label>
          <label>
            Accountable owner / المالك
            <select name="owner_id">
              {users.data?.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.username} · {u.role}
                </option>
              ))}
            </select>
          </label>
          <label>
            Organizational due date / موعد داخلي
            <input name="due" type="date" required />
          </label>
          <button className="primary">Save / حفظ</button>
        </form>
      )}
      <div className="kanban">
        {["Open", "In Progress", "Ready for Retest", "Closed"].map((state) => (
          <section key={state}>
            <h3>
              {state}
              <span>
                {q.data?.filter((f) => f.state === state).length || 0}
              </span>
            </h3>
            {q.data
              ?.filter((f) => f.state === state)
              .map((f) => (
                <article className="panel finding-card" key={f.id}>
                  <small>
                    FND-{f.id} · ASM-{f.assessment_id} · RSK-{f.risk_id}
                  </small>
                  <h3>{f.title}</h3>
                  <p>{f.action}</p>
                  <div className="finding-meta">
                    <span>
                      {users.data?.find((u) => u.id === f.owner_id)?.username}
                    </span>
                    <span>{f.due}</span>
                  </div>
                  {((user.id === f.owner_id &&
                    ["Open", "In Progress"].includes(state)) ||
                    (["Internal Auditor", "GRC Manager"].includes(user.role) &&
                      state === "Ready for Retest")) && (
                    <form
                      onSubmit={(e) => {
                        e.preventDefault();
                        const fdata = new FormData(e.currentTarget);
                        void act(() =>
                          api("/findings/" + f.id + "/transition", "POST", {
                            state:
                              state === "Open"
                                ? "In Progress"
                                : state === "In Progress"
                                  ? "Ready for Retest"
                                  : "Closed",
                            rationale: fdata.get("rationale"),
                          }),
                        );
                      }}
                    >
                      <input
                        name="rationale"
                        minLength={10}
                        required
                        placeholder={t(
                          "Action / retest rationale",
                          "مبررات الإجراء / الاختبار",
                        )}
                      />
                      <button>
                        {state === "Open"
                          ? t("Start action", "بدء الإجراء")
                          : state === "In Progress"
                            ? t("Submit for retest", "إرسال لإعادة الاختبار")
                            : t("Close after retest", "إغلاق بعد الاختبار")}
                      </button>
                    </form>
                  )}
                </article>
              ))}
          </section>
        ))}
      </div>
      {q.error && <Loading error={q.error} />}
    </>
  );
}
function Sources({ t }: { t: T }) {
  const q = useData<DomainRecord[]>("/records/source");
  return (
    <>
      <Title
        title={t("Regulatory source register", "سجل المصادر التنظيمية")}
        subtitle={t(
          "Provenance before interpretation. Source access is not legal validation.",
          "توثيق المصدر يسبق التفسير. الوصول للمصدر لا يعني اعتماداً قانونياً.",
        )}
      />
      <div className="registry-grid">
        {q.data?.map((r) => (
          <article className="panel source-panel" key={r.id}>
            <div className="panel-heading">
              <Globe2 size={22} />
              {badge(String(r.payload.verification_status))}
            </div>
            <h2>{r.title}</h2>
            <p>{String(r.payload.version)}</p>
            <dl>
              {[
                "publisher",
                "last_verified_date",
                "legal_applicability",
                "interpretation",
                "implementation_guidance",
              ].map((k) => (
                <React.Fragment key={k}>
                  <dt>{k.replaceAll("_", " ")}</dt>
                  <dd>{String(r.payload[k])}</dd>
                </React.Fragment>
              ))}
            </dl>
            <a
              href={String(r.payload.official_source_url)}
              target="_blank"
              rel="noreferrer"
            >
              {t("Inspect official source", "فحص المصدر الرسمي")} ↗
            </a>
          </article>
        ))}
      </div>
      {q.error && <Loading error={q.error} />}
    </>
  );
}

const domainInitialStatus: Record<string, string> = {
  policy: "Draft",
  governance: "Draft",
  privacy: "Draft",
  evidence: "Draft",
  vendor: "Open",
  incident: "Open",
  continuity: "Draft",
  training: "Open",
  audit: "Draft",
  gap: "Open",
  remediation: "Open",
};

function transitionOptions(item: WorkItem) {
  if (item.domain === "policy") {
    return (
      {
        Draft: ["Under Review"],
        "Under Review": ["Draft", "Approved"],
        Approved: ["Published", "Draft"],
        Published: ["Expired", "Retired", "Draft"],
        Expired: ["Draft", "Retired"],
        Retired: [],
      }[item.status] || []
    );
  }
  return (
    {
      Draft: ["Under Review", "Open"],
      Open: ["Planned", "In Progress", "Deferred", "Rejected"],
      Planned: ["In Progress", "Deferred"],
      "Under Review": ["Draft", "Approved", "In Progress"],
      Approved: ["In Progress", "Closed"],
      "In Progress": ["Pending Verification", "Deferred"],
      "Pending Verification": ["In Progress", "Closed"],
      Deferred: ["Open", "In Progress"],
      Rejected: ["Open"],
      Closed: ["Open"],
    }[item.status] || []
  );
}

function OperationalCenter({
  domain,
  title,
  subtitle,
  t,
  act,
  user,
}: {
  domain: string;
  title: string;
  subtitle: string;
  t: T;
  act: Act;
  user: User;
}) {
  const q = useData<WorkItem[]>(`/work-items?domain=${domain}`);
  const users = useData<User[]>("/users");
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("All");
  const [sort, setSort] = useState("uid");
  const [selected, setSelected] = useState<WorkItem | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [target, setTarget] = useState("");
  const [rationale, setRationale] = useState("");
  const rows = [...(q.data || [])]
    .filter(
      (item) =>
        (status === "All" || item.status === status) &&
        `${item.uid} ${item.title_ar} ${item.title_en}`
          .toLowerCase()
          .includes(search.toLowerCase()),
    )
    .sort((a, b) =>
      sort === "due"
        ? String(a.due_date || "9999").localeCompare(
            String(b.due_date || "9999"),
          )
        : sort === "status"
          ? a.status.localeCompare(b.status)
          : a.uid.localeCompare(b.uid),
    );
  const statuses = Array.from(
    new Set((q.data || []).map((item) => item.status)),
  ).sort();
  const canCreate = [
    "Super Admin",
    "GRC Manager",
    "GRC Analyst",
    "Compliance Officer",
    "Privacy Officer",
  ].includes(user.role);
  const selectedFresh =
    selected && q.data?.find((item) => item.id === selected.id);

  return (
    <>
      <Title title={title} subtitle={subtitle}>
        {canCreate && (
          <button
            className="primary"
            onClick={() => setShowCreate(!showCreate)}
          >
            <Plus size={16} /> {t("New record", "سجل جديد")}
          </button>
        )}
      </Title>
      {showCreate && (
        <form
          className="panel operational-form"
          onSubmit={(event) => {
            event.preventDefault();
            const values = Object.fromEntries(
              new FormData(event.currentTarget),
            );
            const analyst = users.data?.find(
              (item) => item.username === "analyst",
            );
            const auditor = users.data?.find(
              (item) => item.username === "auditor",
            );
            void act(async () => {
              await api("/work-items", "POST", {
                domain,
                record_type: values.record_type,
                title_ar: values.title_ar,
                title_en: values.title_en,
                status: domainInitialStatus[domain] || "Draft",
                owner_id: user.id,
                reviewer_id: analyst?.id || null,
                approver_id: auditor?.id || null,
                due_date: values.due_date || null,
                payload: {
                  summary: values.summary,
                  simulation_label:
                    "SIMULATED DATA — NOT REAL ORGANIZATIONAL EVIDENCE",
                },
              });
              setShowCreate(false);
            });
          }}
        >
          <div className="form-heading">
            <div>
              <h2>{t("Create operational record", "إنشاء سجل تشغيلي")}</h2>
              <p>
                {t(
                  "The signed-in user becomes the accountable owner.",
                  "يصبح المستخدم الحالي المالك المسؤول.",
                )}
              </p>
            </div>
            <button type="button" onClick={() => setShowCreate(false)}>
              <X size={17} />
            </button>
          </div>
          <div className="form-grid">
            <label>
              {t("Arabic title", "العنوان العربي")}
              <input name="title_ar" minLength={3} required />
            </label>
            <label>
              {t("English title", "العنوان الإنجليزي")}
              <input name="title_en" minLength={3} required dir="ltr" />
            </label>
            <label>
              {t("Record type", "نوع السجل")}
              <input
                name="record_type"
                defaultValue={`${domain}_record`}
                required
                dir="ltr"
              />
            </label>
            <label>
              {t("Due date", "تاريخ الاستحقاق")}
              <input name="due_date" type="date" />
            </label>
          </div>
          <label>
            {t("Summary", "الملخص")}
            <textarea name="summary" minLength={12} required />
          </label>
          <button className="primary">
            {t("Create record", "إنشاء السجل")}
          </button>
        </form>
      )}
      <section className="panel operational-list">
        <div className="toolbar">
          <label className="search">
            <Search size={16} />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={t("Search ID or title", "البحث بالمعرف أو العنوان")}
            />
          </label>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            aria-label={t("Filter status", "تصفية الحالة")}
          >
            <option value="All">{t("All statuses", "كل الحالات")}</option>
            {statuses.map((value) => (
              <option key={value}>{value}</option>
            ))}
          </select>
          <select
            value={sort}
            onChange={(e) => setSort(e.target.value)}
            aria-label={t("Sort", "الترتيب")}
          >
            <option value="uid">{t("Sort by ID", "ترتيب بالمعرف")}</option>
            <option value="due">
              {t("Sort by due date", "ترتيب بالاستحقاق")}
            </option>
            <option value="status">
              {t("Sort by status", "ترتيب بالحالة")}
            </option>
          </select>
          <span className="record-count">
            {rows.length} {t("records", "سجلات")}
          </span>
        </div>
        {q.error && <Loading error={q.error} />}
        {!q.data && !q.error && <Loading />}
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>{t("Record", "السجل")}</th>
                <th>{t("Owner", "المالك")}</th>
                <th>{t("Due", "الاستحقاق")}</th>
                <th>{t("Status", "الحالة")}</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((item) => (
                <tr
                  key={item.id}
                  className={selected?.id === item.id ? "selected-row" : ""}
                  onClick={() => {
                    setSelected(item);
                    setTarget("");
                    setRationale("");
                  }}
                >
                  <td>
                    <button className="row-link">
                      <b>{t(item.title_en, item.title_ar)}</b>
                      <small>
                        {item.uid} · {item.record_type.replaceAll("_", " ")}
                      </small>
                    </button>
                  </td>
                  <td>{item.owner}</td>
                  <td className="num" dir="ltr">
                    {item.due_date || "—"}
                  </td>
                  <td>{badge(item.status)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {q.data && rows.length === 0 && (
          <p className="empty">
            {t(
              "No records match this view.",
              "لا توجد سجلات مطابقة لهذا العرض.",
            )}
          </p>
        )}
      </section>
      {selectedFresh && (
        <section className="panel record-view">
          <div className="panel-heading">
            <div>
              <small>{selectedFresh.uid}</small>
              <h2>{t(selectedFresh.title_en, selectedFresh.title_ar)}</h2>
              <p>{selectedFresh.simulation_label}</p>
            </div>
            <button
              onClick={() => setSelected(null)}
              aria-label={t("Close details", "إغلاق التفاصيل")}
            >
              <X size={18} />
            </button>
          </div>
          <div className="record-summary">
            <div>
              <span>{t("Owner", "المالك")}</span>
              <b>{selectedFresh.owner}</b>
            </div>
            <div>
              <span>{t("Reviewer", "المراجع")}</span>
              <b>{selectedFresh.reviewer || "—"}</b>
            </div>
            <div>
              <span>{t("Approver", "المعتمد")}</span>
              <b>{selectedFresh.approver || "—"}</b>
            </div>
            <div>
              <span>{t("Version", "الإصدار")}</span>
              <b className="num">{selectedFresh.version}</b>
            </div>
          </div>
          <dl className="record-details">
            {Object.entries(selectedFresh.payload).map(([key, value]) => (
              <React.Fragment key={key}>
                <dt>{key.replaceAll("_", " ")}</dt>
                <dd>{text(value)}</dd>
              </React.Fragment>
            ))}
          </dl>
          {transitionOptions(selectedFresh).length > 0 && (
            <form
              className="transition-form"
              onSubmit={(event) => {
                event.preventDefault();
                if (!target) return;
                void act(async () => {
                  await api(
                    `/work-items/${selectedFresh.id}/transition`,
                    "POST",
                    { status: target, rationale },
                  );
                  setTarget("");
                  setRationale("");
                });
              }}
            >
              <h3>{t("Lifecycle action", "إجراء دورة الحياة")}</h3>
              <select
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                required
              >
                <option value="">
                  {t("Select next state", "اختر الحالة التالية")}
                </option>
                {transitionOptions(selectedFresh).map((value) => (
                  <option key={value}>{value}</option>
                ))}
              </select>
              <textarea
                value={rationale}
                onChange={(e) => setRationale(e.target.value)}
                minLength={12}
                placeholder={t(
                  "Document the reason and evidence considered",
                  "وثّق السبب والأدلة التي تمت مراجعتها",
                )}
                required
              />
              <button className="primary">
                {t("Apply transition", "تنفيذ الانتقال")}
              </button>
            </form>
          )}
        </section>
      )}
    </>
  );
}

function Acknowledgements({ t, act }: { t: T; act: Act }) {
  const q = useData<
    Array<{
      id: number;
      policy_id: number;
      subject_ref: string;
      subject_name: string;
      department: string;
      status: string;
      acknowledged_at: string | null;
    }>
  >("/policy-acknowledgements");
  return (
    <>
      <Title
        title={t("Policy acknowledgement", "إقرار السياسات")}
        subtitle={t(
          "Representative fictional assignments; metrics use only the displayed sample.",
          "تكليفات افتراضية بعينة ممثلة؛ تحتسب المؤشرات من العينة المعروضة فقط.",
        )}
      />
      <section className="panel">
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>{t("Employee", "الموظف")}</th>
                <th>{t("Department", "الإدارة")}</th>
                <th>{t("Policy", "السياسة")}</th>
                <th>{t("Status", "الحالة")}</th>
                <th>{t("Action", "الإجراء")}</th>
              </tr>
            </thead>
            <tbody>
              {q.data?.map((item) => (
                <tr key={item.id}>
                  <td>
                    <b>{item.subject_name}</b>
                    <small>{item.subject_ref}</small>
                  </td>
                  <td>{item.department}</td>
                  <td className="num">#{item.policy_id}</td>
                  <td>{badge(item.status)}</td>
                  <td>
                    {item.status !== "Acknowledged" ? (
                      <button
                        onClick={() =>
                          void act(() =>
                            api(
                              `/policy-acknowledgements/${item.id}/acknowledge`,
                              "POST",
                              { subject_ref: item.subject_ref },
                            ),
                          )
                        }
                      >
                        {t("Record acknowledgement", "تسجيل الإقرار")}
                      </button>
                    ) : (
                      <span>
                        {item.acknowledged_at
                          ? new Date(item.acknowledged_at).toLocaleDateString()
                          : "—"}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}

function SettingsAndRoles({ t, act, user }: { t: T; act: Act; user: User }) {
  const config = useData<DomainRecord[]>("/records/configuration");
  const users = useData<User[]>("/users");
  const roles = [
    "Super Admin",
    "GRC Manager",
    "GRC Analyst",
    "Compliance Officer",
    "Risk Manager",
    "Risk Owner",
    "Privacy Officer",
    "Control Owner",
    "Internal Auditor",
    "Executive Viewer",
  ];
  return (
    <>
      <Title
        title={t("Settings & role management", "الإعدادات وإدارة الصلاحيات")}
        subtitle={t(
          "Organization scope and server-enforced demo roles.",
          "نطاق المنشأة وأدوار تجريبية مفروضة من الخادم.",
        )}
      />
      <section className="settings-section">
        <div>
          <h2>{t("Organization", "المنشأة")}</h2>
          <p>
            {t(
              "The simulation context used by every module and report.",
              "سياق المحاكاة المستخدم في كل وحدة وتقرير.",
            )}
          </p>
        </div>
        <article className="panel">
          <dl className="record-details">
            {Object.entries(config.data?.[0]?.payload || {}).map(
              ([key, value]) => (
                <React.Fragment key={key}>
                  <dt>{key.replaceAll("_", " ")}</dt>
                  <dd>{text(value)}</dd>
                </React.Fragment>
              ),
            )}
          </dl>
        </article>
      </section>
      <section className="settings-section">
        <div>
          <h2>{t("Users and roles", "المستخدمون والأدوار")}</h2>
          <p>
            {t(
              "Only a Super Admin may change a role. Self-demotion is blocked.",
              "لا يغير الدور إلا المدير العام، ويُمنع تغيير دوره ذاتياً.",
            )}
          </p>
        </div>
        <article className="panel">
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>{t("Account", "الحساب")}</th>
                  <th>{t("Role", "الدور")}</th>
                </tr>
              </thead>
              <tbody>
                {users.data?.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <b>{item.username}</b>
                      <small>USR-{String(item.id).padStart(3, "0")}</small>
                    </td>
                    <td>
                      {user.role === "Super Admin" && user.id !== item.id ? (
                        <select
                          value={item.role}
                          onChange={(event) =>
                            void act(() =>
                              api(`/users/${item.id}/role`, "PUT", {
                                role: event.target.value,
                              }),
                            )
                          }
                        >
                          {roles.map((role) => (
                            <option key={role}>{role}</option>
                          ))}
                        </select>
                      ) : (
                        badge(item.role)
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>
      </section>
    </>
  );
}

function Registry({
  t,
  title,
  subtitle,
  kinds,
}: {
  t: T;
  title: string;
  subtitle: string;
  kinds: string[];
}) {
  const [kind, setKind] = useState(kinds[0]);
  const [search, setSearch] = useState("");
  const q = useData<DomainRecord[]>("/records/" + kind);
  return (
    <>
      <Title title={title} subtitle={subtitle} />
      <div className="tabs">
        {kinds.map((k) => (
          <button
            key={k}
            className={kind === k ? "active" : ""}
            onClick={() => setKind(k)}
          >
            {k.replaceAll("_", " ").toUpperCase()}
          </button>
        ))}
      </div>
      <div className="panel">
        <div className="toolbar">
          <label className="search">
            <Search size={16} />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={t("Search registry", "البحث في السجل")}
            />
          </label>
          <span className="badge">
            {t("Read-only baseline registry", "سجل أساسي للقراءة فقط")}
          </span>
        </div>
        {q.data
          ?.filter((r) =>
            (r.title + r.department)
              .toLowerCase()
              .includes(search.toLowerCase()),
          )
          .map((r) => (
            <details className="registry-row" key={r.id}>
              <summary>
                <div>
                  <b>{r.title}</b>
                  <small>
                    {r.department} · #{r.id}
                  </small>
                </div>
                <span className="badge">
                  {String(
                    r.payload.status ||
                      r.payload.state ||
                      r.payload.classification ||
                      "Synthetic",
                  )}
                </span>
              </summary>
              <dl className="record-details">
                {Object.entries(r.payload).map(([k, v]) => (
                  <React.Fragment key={k}>
                    <dt>{k.replaceAll("_", " ")}</dt>
                    <dd>{text(v)}</dd>
                  </React.Fragment>
                ))}
              </dl>
            </details>
          ))}
        {q.error && <Loading error={q.error} />}
      </div>
    </>
  );
}
function Audit({ t, act }: { t: T; act: Act }) {
  const q = useData<
    {
      id: number;
      actor: string;
      action: string;
      target: string;
      created: string;
      digest: string;
    }[]
  >("/activity");
  const [result, setResult] = useState("");
  return (
    <>
      <Title
        title={t(
          "Tamper-evident activity trail",
          "سجل النشاط القابل لكشف العبث",
        )}
        subtitle={t(
          "Chained SHA-256 event records. External head anchoring is required against administrator rewrites.",
          "سجلات مترابطة بـ SHA-256. يلزم تثبيت بصمة خارجية لمقاومة إعادة الكتابة الإدارية.",
        )}
      >
        <button
          className="primary"
          onClick={() =>
            void act(async () => {
              const r = await api<{ valid: boolean; count: number }>(
                "/activity/verify",
              );
              setResult(
                `${r.valid ? "Valid chain / سلسلة سليمة" : "INTEGRITY FAILURE"} · ${r.count} events`,
              );
            })
          }
        >
          <Check size={16} />
          {t("Verify chain", "التحقق من السلسلة")}
        </button>
      </Title>
      {result && <div className="notice">{result}</div>}
      <div className="panel">
        {q.error ? (
          <Loading error={q.error} />
        ) : (
          <div className="timeline">
            {q.data?.map((e) => (
              <div key={e.id}>
                <span className="timeline-dot" />
                <div>
                  <b>{e.action}</b>
                  <p>
                    {e.actor} → {e.target}
                  </p>
                  <code>{e.digest.slice(0, 24)}…</code>
                </div>
                <time>{new Date(e.created).toLocaleString()}</time>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
function Reports({ t, act }: { t: T; act: Act }) {
  const [report, setReport] = useState<Record<string, unknown> | null>(null);
  const identity = useData<User>("/me");
  return (
    <>
      <Title
        title={t("Management reporting", "تقارير الإدارة")}
        subtitle={t(
          "Scoped reports include methodology, source provenance and evidence manifests.",
          "تقارير محددة النطاق تتضمن المنهجية والمصادر وفهرس الأدلة.",
        )}
      />
      <div className="registry-grid">
        {identity.data &&
          ["Super Admin", "GRC Manager", "Internal Auditor"].includes(
            identity.data.role,
          ) && (
            <article className="panel report-card">
              <FolderLock size={36} />
              <h2>{t("Evidence audit pack", "حزمة أدلة التدقيق")}</h2>
              <p>
                {t(
                  "Authorized export with decrypted synthetic documents, source references and SHA-256 manifest. Protect the downloaded archive.",
                  "تصدير مصرح به يتضمن المستندات الاصطناعية بعد فك التشفير ومراجع المصادر وفهرس البصمات. احمِ الملف المحمّل.",
                )}
              </p>
              <a
                className="primary"
                href={
                  isDemoMode
                    ? publicAsset("downloads/mizan-demo-audit-pack.zip")
                    : "/api/reports/audit-pack.zip"
                }
              >
                <Download size={16} />
                {t("Export audit pack", "تصدير حزمة التدقيق")}
              </a>
            </article>
          )}
        <article className="panel report-card">
          <FileText size={36} />
          <h2>{t("Executive management report", "تقرير الإدارة التنفيذي")}</h2>
          <p>
            {t(
              "Live assessment state, findings and evidence references. JSON export; browser print available.",
              "حالة التقييمات والفجوات ومراجع الأدلة. تصدير JSON وطباعة المتصفح.",
            )}
          </p>
          <button
            className="primary"
            onClick={() =>
              void act(async () =>
                setReport(
                  await api<Record<string, unknown>>("/reports/management"),
                ),
              )
            }
          >
            {t("Generate report", "إنشاء التقرير")}
          </button>
        </article>
        <article className="panel report-card">
          <ShieldAlert size={36} />
          <h2>{t("Risk register export", "تصدير سجل المخاطر")}</h2>
          <p>
            {t(
              "UTF-8 CSV with inherent and residual scores, treatment and export timestamps.",
              "ملف CSV مع درجات المخاطر الكامنة والمتبقية والمعالجة ووقت التصدير.",
            )}
          </p>
          <a
            className="button"
            href={
              isDemoMode
                ? publicAsset("downloads/mizan-demo-risks.csv")
                : "/api/reports/risks.csv"
            }
          >
            <Download size={16} />
            {t("Export CSV", "تصدير CSV")}
          </a>
        </article>
      </div>
      {report && (
        <article className="panel report-preview">
          <div className="panel-heading">
            <h2>{String(report.title)}</h2>
            <div className="inline-badges">
              <button onClick={() => window.print()}>
                {t("Print / save PDF", "طباعة / حفظ PDF")}
              </button>
              <button
                onClick={() => {
                  const url = URL.createObjectURL(
                    new Blob([JSON.stringify(report, null, 2)], {
                      type: "application/json",
                    }),
                  );
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = "mizan-management-report.json";
                  a.click();
                  URL.revokeObjectURL(url);
                }}
              >
                <Download size={16} />
                JSON
              </button>
            </div>
          </div>
          <p>{String(report.scope)}</p>
          <p>{String(report.limitations)}</p>
          <pre>{JSON.stringify(report, null, 2)}</pre>
        </article>
      )}
    </>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={qc}>
      {isDemoMode ? (
        <HashRouter>
          <App />
        </HashRouter>
      ) : (
        <BrowserRouter>
          <App />
        </BrowserRouter>
      )}
    </QueryClientProvider>
  </React.StrictMode>,
);
