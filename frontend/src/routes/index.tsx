import { createFileRoute, Link } from "@tanstack/react-router";
import { motion, useScroll, useTransform, useMotionValue, useSpring } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import {
  ArrowRight,
  ArrowUpRight,
  BarChart3,
  Building2,
  CheckCircle2,
  ChevronRight,
  Database,
  FileText,
  Github,
  GraduationCap,
  HeartPulse,
  Landmark,
  Layers,
  Linkedin,
  Lock,
  Mail,
  MessageSquare,
  Minus,
  Network,
  Radio,
  Search,
  ShieldCheck,
  ShoppingBag,
  Sparkles,
  Target,
  TrendingUp,
  Twitter,
  Users,
  Wrench,
} from "lucide-react";
import { Logo, LogoMark } from "@/components/brand/Logo";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { AnimatedNumber } from "@/components/ui/AnimatedNumber";
import { DemoModal } from "@/components/landing/DemoModal";
import { cn } from "@/lib/utils";
import heroImage from "@/assets/hero-business.jpg";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "CustomerLens — Turn Customer Data Into Business Growth" },
      {
        name: "description",
        content:
          "CustomerLens unifies customer data, documents, transactions, and business insights into one intelligent workspace to help organizations understand customers, predict opportunities, reduce churn, and decide faster.",
      },
      { property: "og:title", content: "CustomerLens — Turn Customer Data Into Business Growth" },
      {
        property: "og:description",
        content:
          "CustomerLens unifies customer data, documents, transactions, and business insights into one intelligent workspace to help organizations understand customers, predict opportunities, reduce churn, and decide faster.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: LandingPage,
});

// ---------------- Content ----------------

const NAV = [
  { label: "Platform", href: "#platform" },
  { label: "Solutions", href: "#solutions" },
  { label: "Industries", href: "#industries" },
  { label: "Resources", href: "#resources" },
  { label: "Pricing", href: "/pricing" },
  { label: "Company", href: "#company" },
];

const INDUSTRIES = [
  { icon: Landmark, name: "Financial Services", desc: "Fraud, risk, wealth 360." },
  { icon: HeartPulse, name: "Healthcare", desc: "Patient journeys, adherence." },
  { icon: ShoppingBag, name: "Retail", desc: "Loyalty, basket, LTV." },
  { icon: Wrench, name: "Manufacturing", desc: "OEM, service, warranty." },
  { icon: ShieldCheck, name: "Insurance", desc: "Underwriting, retention." },
  { icon: Radio, name: "Telecommunications", desc: "Churn, network experience." },
  { icon: GraduationCap, name: "Education", desc: "Enrollment, outcomes." },
  { icon: Layers, name: "SaaS", desc: "Product-led growth signals." },
];

const WORKFLOW = [
  { title: "Upload Customer Data", desc: "Bring CSVs, warehouses, and SaaS sources into one workspace." },
  { title: "Clean & Organize", desc: "Automatic schema mapping, dedupe, and quality scoring." },
  { title: "Analyze Business Data", desc: "Segments, cohorts, and revenue drivers surface in minutes." },
  { title: "Generate Customer Profiles", desc: "Unified 360° records with transactions, tickets, and documents." },
  { title: "Ask Business Questions", desc: "Natural-language answers with cited evidence and confidence." },
  { title: "Receive Actionable Insights", desc: "Ranked recommendations tied to revenue and retention." },
  { title: "Predict Customer Behaviour", desc: "Churn, LTV, propensity — with explainable drivers." },
  { title: "Make Better Decisions", desc: "Ship the next best action to the teams that own it." },
];

const FEATURES = [
  { icon: Users, title: "Customer 360", desc: "One record per customer stitched from every source." },
  { icon: TrendingUp, title: "Predictive Analytics", desc: "Forecast churn, LTV, and revenue with explainability." },
  { icon: BarChart3, title: "Business Intelligence", desc: "Dashboards leadership actually opens on Monday." },
  { icon: FileText, title: "Document Intelligence", desc: "Contracts, tickets, and PDFs turned into signals." },
  { icon: Search, title: "Knowledge Search", desc: "Cited answers across your entire business corpus." },
  { icon: Layers, title: "Interactive Dashboards", desc: "Drill, filter, and share without a data ticket." },
  { icon: Sparkles, title: "Smart Reports", desc: "Executive briefs generated from live data." },
  { icon: ShieldCheck, title: "Enterprise Security", desc: "SOC 2, GDPR, SSO, RBAC, audit logs." },
];

const METRICS = [
  { value: 12, suffix: "M+", label: "Customer Records" },
  { value: 150, suffix: "M+", label: "Transactions" },
  { value: 2, suffix: "M+", label: "Business Insights" },
  { value: 97, suffix: "%", label: "Prediction Accuracy" },
  { value: 2, prefix: "<", suffix: "s", label: "Avg. Response Time" },
];

const SECURITY = [
  { icon: ShieldCheck, t: "SOC 2 Type II" },
  { icon: Lock, t: "GDPR Compliant" },
  { icon: Users, t: "Role-Based Access" },
  { icon: Database, t: "Encrypted Storage" },
  { icon: FileText, t: "Full Audit Logs" },
  { icon: Building2, t: "Private Deployment" },
];

// ---------------- Page ----------------

function LandingPage() {
  const [demoOpen, setDemoOpen] = useState(false);

  return (
    <div className="dark relative min-h-screen w-full overflow-x-clip bg-[#090B14] text-white antialiased">
      <BackgroundFX />
      <Nav onDemoOpen={() => setDemoOpen(true)} />
      <Hero onDemoOpen={() => setDemoOpen(true)} />
      <IndustriesSection />
      <PlatformPreview />
      <WorkflowSection />
      <FeaturesSection />
      <BusinessImpactSection />
      <MetricsSection />
      <SecuritySection />
      <FinalCTA onDemoOpen={() => setDemoOpen(true)} />
      <Footer />
      <DemoModal open={demoOpen} onClose={() => setDemoOpen(false)} />
    </div>
  );
}

// ---------------- Global background ----------------

function BackgroundFX() {
  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      <div
        className="absolute inset-0"
        style={{
          backgroundImage:
            "radial-gradient(circle at 12% 8%, rgba(99,102,241,0.22), transparent 42%), radial-gradient(circle at 88% 12%, rgba(34,211,238,0.14), transparent 45%), radial-gradient(circle at 50% 100%, rgba(139,92,246,0.18), transparent 50%)",
        }}
      />
      <div className="absolute inset-0 opacity-[0.05] [background-image:linear-gradient(to_right,#ffffff_1px,transparent_1px),linear-gradient(to_bottom,#ffffff_1px,transparent_1px)] [background-size:64px_64px] [mask-image:radial-gradient(ellipse_at_center,black_40%,transparent_75%)]" />
      <div className="absolute -top-40 left-1/3 h-[520px] w-[520px] rounded-full bg-indigo-600/25 blur-[130px] animate-float-slow" />
      <div
        className="absolute top-1/2 -right-40 h-[560px] w-[560px] rounded-full bg-violet-600/20 blur-[130px] animate-float-slow"
        style={{ animationDelay: "-6s" }}
      />
    </div>
  );
}

// ---------------- Navigation ----------------

function Nav({ onDemoOpen }: { onDemoOpen: () => void }) {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={cn(
        "fixed inset-x-0 top-0 z-40 transition-all duration-300",
        scrolled ? "border-b border-white/[0.06] bg-[#090B14]/70 backdrop-blur-xl" : "bg-transparent",
      )}
    >
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        <Link to="/" className="flex items-center">
          <Logo />
        </Link>

        <nav className="hidden items-center gap-1 lg:flex">
          {NAV.map((n) => (
            <a
              key={n.label}
              href={n.href}
              className="rounded-md px-3 py-2 text-sm text-white/70 transition hover:bg-white/5 hover:text-white"
            >
              {n.label}
            </a>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <Link
            to="/login"
            className="hidden rounded-md px-3 py-2 text-sm font-medium text-white/80 transition hover:text-white sm:inline-flex"
          >
            Sign In
          </Link>
          <Button
            onClick={onDemoOpen}
            size="sm"
            className="h-9 gap-1.5 bg-brand-gradient px-4 text-primary-foreground shadow-elegant hover:opacity-95"
          >
            Book Demo <ArrowRight className="h-3.5 w-3.5" />
          </Button>
          <button
            onClick={() => setOpen((v) => !v)}
            className="ml-1 inline-flex h-9 w-9 items-center justify-center rounded-md border border-white/10 text-white/80 lg:hidden"
            aria-label="Menu"
          >
            <Layers className="h-4 w-4" />
          </button>
        </div>
      </div>
      {open && (
        <div className="border-t border-white/[0.06] bg-[#090B14]/95 px-6 py-3 lg:hidden">
          <div className="flex flex-col gap-1">
            {NAV.map((n) => (
              <a
                key={n.label}
                href={n.href}
                onClick={() => setOpen(false)}
                className="rounded-md px-2 py-2 text-sm text-white/80 hover:bg-white/5"
              >
                {n.label}
              </a>
            ))}
          </div>
        </div>
      )}
    </header>
  );
}

// ---------------- Hero ----------------

function Hero({ onDemoOpen }: { onDemoOpen: () => void }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollY } = useScroll();
  const imgY = useTransform(scrollY, [0, 800], [0, 120]);
  const imgScale = useTransform(scrollY, [0, 800], [1, 1.08]);

  // Mouse parallax on overlays
  const mx = useMotionValue(0);
  const my = useMotionValue(0);
  const sx = useSpring(mx, { stiffness: 60, damping: 20 });
  const sy = useSpring(my, { stiffness: 60, damping: 20 });

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const onMove = (e: MouseEvent) => {
      const r = el.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - 0.5;
      const y = (e.clientY - r.top) / r.height - 0.5;
      mx.set(x * 20);
      my.set(y * 20);
    };
    el.addEventListener("mousemove", onMove);
    return () => el.removeEventListener("mousemove", onMove);
  }, [mx, my]);

  return (
    <section ref={containerRef} className="relative overflow-hidden pt-32 pb-20 md:pt-40 md:pb-28">
      <div className="mx-auto max-w-7xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mx-auto max-w-4xl text-center"
        >
          <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs text-white/70 backdrop-blur">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
            New — Customer Intelligence Platform · v4
          </div>
          <h1 className="mt-6 text-4xl font-semibold leading-[1.05] tracking-tight text-white md:text-6xl lg:text-7xl">
            Turn Customer Data Into
            <br />
            <span className="text-brand-gradient">Business Growth</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-base leading-relaxed text-white/65 md:text-lg">
            CustomerLens unifies customer data, documents, transactions, and business insights into one
            intelligent workspace — helping organizations understand customers, predict opportunities,
            reduce churn, and make smarter decisions.
          </p>
          <div className="mt-9 flex flex-wrap items-center justify-center gap-3">
            <Button
              onClick={onDemoOpen}
              size="lg"
              className="group h-12 gap-2 bg-brand-gradient px-6 text-primary-foreground shadow-elegant hover:opacity-95"
            >
              Book a Live Demo
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </Button>
            <a href="#platform">
              <Button
                size="lg"
                variant="outline"
                className="h-12 gap-2 border-white/15 bg-white/[0.04] text-white backdrop-blur hover:bg-white/[0.08]"
              >
                Explore Platform <ChevronRight className="h-4 w-4" />
              </Button>
            </a>
          </div>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-xs text-white/45">
            <span className="inline-flex items-center gap-1.5">
              <ShieldCheck className="h-3.5 w-3.5" /> SOC 2 Type II
            </span>
            <span className="inline-flex items-center gap-1.5">
              <Lock className="h-3.5 w-3.5" /> GDPR &amp; HIPAA
            </span>
            <span className="inline-flex items-center gap-1.5">
              <Building2 className="h-3.5 w-3.5" /> Deployed in 40+ enterprises
            </span>
          </div>
        </motion.div>

        {/* Hero visual */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, delay: 0.2 }}
          className="relative mx-auto mt-16 max-w-6xl"
        >
          <div className="absolute -inset-6 rounded-[2rem] bg-brand-gradient opacity-25 blur-3xl" />
          <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-[#0B0E1A] shadow-2xl">
            <div className="relative aspect-[16/9] w-full overflow-hidden">
              <motion.img
                src={heroImage}
                alt="Business executives collaborating on customer analytics dashboards"
                width={1600}
                height={900}
                className="h-full w-full object-cover"
                style={{ y: imgY, scale: imgScale }}
              />
              {/* Gradient wash */}
              <div className="absolute inset-0 bg-gradient-to-tr from-[#090B14] via-transparent to-indigo-900/30" />
              <div className="absolute inset-0 bg-gradient-to-t from-[#090B14] via-transparent to-transparent" />

              {/* Floating overlays with mouse parallax */}
              <motion.div
                style={{ x: sx, y: sy }}
                className="absolute left-4 top-6 hidden md:block"
              >
                <FloatingChart />
              </motion.div>
              <motion.div
                style={{ x: useTransform(sx, (v) => -v), y: useTransform(sy, (v) => -v) }}
                className="absolute right-4 top-8 hidden md:block"
              >
                <FloatingInsight />
              </motion.div>
              <motion.div
                style={{ x: sx, y: useTransform(sy, (v) => -v) }}
                className="absolute bottom-6 left-8 hidden md:block"
              >
                <FloatingKPI />
              </motion.div>
              <motion.div
                style={{ x: useTransform(sx, (v) => -v), y: sy }}
                className="absolute bottom-8 right-6 hidden md:block"
              >
                <FloatingNetwork />
              </motion.div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

function FloatingChart() {
  const bars = [24, 44, 32, 60, 48, 72, 66, 88];
  return (
    <div className="w-56 rounded-xl border border-white/10 bg-[#0B0E1A]/80 p-3 shadow-2xl backdrop-blur-xl">
      <div className="flex items-center justify-between text-[10px] text-white/60">
        <span className="font-semibold uppercase tracking-wider">Revenue · MTD</span>
        <span className="text-emerald-400">+18.2%</span>
      </div>
      <div className="mt-3 flex h-16 items-end gap-1">
        {bars.map((h, i) => (
          <motion.div
            key={i}
            initial={{ height: 0 }}
            animate={{ height: `${h}%` }}
            transition={{ duration: 0.8, delay: 0.4 + i * 0.06 }}
            className="flex-1 rounded-sm bg-gradient-to-t from-indigo-600 to-cyan-400"
          />
        ))}
      </div>
    </div>
  );
}

function FloatingInsight() {
  return (
    <div className="w-64 rounded-xl border border-white/10 bg-[#0B0E1A]/85 p-4 shadow-2xl backdrop-blur-xl">
      <div className="flex items-center gap-2 text-[10px] font-semibold uppercase tracking-wider text-white/60">
        <Target className="h-3 w-3 text-cyan-400" /> Opportunity · Confidence 94%
      </div>
      <div className="mt-2 text-sm font-medium text-white">
        Expand Premium onboarding to LATAM.
      </div>
      <div className="mt-1 text-xs text-white/50">Projected +$2.3M ARR · 62 days</div>
    </div>
  );
}

function FloatingKPI() {
  return (
    <div className="flex gap-2">
      {[
        { l: "Customers", v: "1.24M", d: "+3.2%" },
        { l: "Churn", v: "2.1%", d: "−0.4pt" },
      ].map((k) => (
        <div key={k.l} className="rounded-xl border border-white/10 bg-[#0B0E1A]/85 p-3 shadow-2xl backdrop-blur-xl">
          <div className="text-[9px] uppercase tracking-wider text-white/50">{k.l}</div>
          <div className="mt-0.5 text-lg font-bold text-white">{k.v}</div>
          <div className="text-[10px] text-emerald-400">{k.d}</div>
        </div>
      ))}
    </div>
  );
}

function FloatingNetwork() {
  return (
    <div className="w-48 rounded-xl border border-white/10 bg-[#0B0E1A]/80 p-3 shadow-2xl backdrop-blur-xl">
      <div className="mb-2 flex items-center gap-2 text-[10px] font-semibold uppercase tracking-wider text-white/60">
        <Network className="h-3 w-3 text-violet-400" /> Customer Graph
      </div>
      <svg viewBox="0 0 160 70" className="h-14 w-full">
        <defs>
          <linearGradient id="nline" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#6366F1" />
            <stop offset="100%" stopColor="#22D3EE" />
          </linearGradient>
        </defs>
        {[
          [20, 20, 60, 40],
          [60, 40, 100, 15],
          [60, 40, 110, 55],
          [100, 15, 140, 30],
          [110, 55, 140, 30],
        ].map(([x1, y1, x2, y2], i) => (
          <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="url(#nline)" strokeWidth="0.8" opacity="0.7" />
        ))}
        {[
          [20, 20], [60, 40], [100, 15], [110, 55], [140, 30],
        ].map(([cx, cy], i) => (
          <circle key={i} cx={cx} cy={cy} r="3" fill="url(#nline)" />
        ))}
      </svg>
    </div>
  );
}

// ---------------- Industries ----------------

function IndustriesSection() {
  return (
    <Section eyebrow="Trust" title="Trusted Across Industries" desc="From regulated finance to retail loyalty, teams build on CustomerLens.">
      <div className="mt-12 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {INDUSTRIES.map((ind, i) => (
          <motion.div
            key={ind.name}
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-60px" }}
            transition={{ duration: 0.35, delay: i * 0.04 }}
          >
            <div className="group relative h-full overflow-hidden rounded-2xl border border-white/[0.08] bg-white/[0.02] p-5 transition-all hover:-translate-y-1 hover:border-white/20 hover:bg-white/[0.04] hover:shadow-[0_20px_60px_-20px_rgba(99,102,241,0.4)]">
              <div className="absolute inset-x-0 -top-px h-px bg-gradient-to-r from-transparent via-white/30 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
              <div className="inline-flex rounded-xl bg-white/[0.04] p-2.5 ring-1 ring-white/10 transition-colors group-hover:bg-brand-gradient">
                <ind.icon className="h-5 w-5 text-white/80 transition-colors group-hover:text-white" />
              </div>
              <div className="mt-4 text-sm font-semibold text-white">{ind.name}</div>
              <div className="mt-1 text-xs text-white/50">{ind.desc}</div>
            </div>
          </motion.div>
        ))}
      </div>
    </Section>
  );
}

// ---------------- Interactive Platform Preview ----------------

const PREVIEW_TABS = [
  { key: "dashboard", label: "Dashboard" },
  { key: "customer", label: "Customer 360" },
  { key: "analytics", label: "Analytics" },
  { key: "copilot", label: "AI Copilot" },
  { key: "predictions", label: "Predictions" },
  { key: "reports", label: "Reports" },
] as const;

type PreviewKey = (typeof PREVIEW_TABS)[number]["key"];

function PlatformPreview() {
  const [tab, setTab] = useState<PreviewKey>("dashboard");
  return (
    <section id="platform" className="relative mx-auto max-w-7xl scroll-mt-20 px-6 py-24 md:py-32">
      <SectionHeader
        eyebrow="Platform"
        title="One workspace for every customer decision"
        desc="Move between analytics, profiles, predictions, and reports without leaving context."
      />
      <div className="mt-12 flex justify-center">
        <div className="flex flex-wrap items-center justify-center gap-1 rounded-xl border border-white/10 bg-white/[0.03] p-1 backdrop-blur">
          {PREVIEW_TABS.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={cn(
                "relative rounded-lg px-3.5 py-2 text-sm font-medium transition-colors",
                tab === t.key ? "text-white" : "text-white/60 hover:text-white",
              )}
            >
              {tab === t.key && (
                <motion.div
                  layoutId="tab-pill"
                  className="absolute inset-0 rounded-lg bg-brand-gradient shadow-elegant"
                  transition={{ type: "spring", stiffness: 300, damping: 26 }}
                />
              )}
              <span className="relative">{t.label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="relative mx-auto mt-10 max-w-5xl">
        <div className="absolute -inset-6 rounded-3xl bg-brand-gradient opacity-20 blur-3xl" />
        <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-[#0B0E1A] shadow-2xl">
          {/* Browser chrome */}
          <div className="flex items-center gap-2 border-b border-white/[0.06] bg-black/30 px-4 py-2.5">
            <div className="flex gap-1.5">
              <div className="h-2.5 w-2.5 rounded-full bg-red-500/70" />
              <div className="h-2.5 w-2.5 rounded-full bg-amber-500/70" />
              <div className="h-2.5 w-2.5 rounded-full bg-emerald-500/70" />
            </div>
            <div className="mx-auto flex items-center gap-2 rounded-md border border-white/10 bg-white/[0.03] px-3 py-1 text-[11px] text-white/50">
              <Lock className="h-3 w-3" /> app.customerlens.ai/{tab}
            </div>
          </div>
          <div className="relative aspect-[16/9] w-full">
            <motion.div
              key={tab}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.35 }}
              className="absolute inset-0 p-6 md:p-8"
            >
              <PreviewSurface tab={tab} />
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
}

function PreviewSurface({ tab }: { tab: PreviewKey }) {
  if (tab === "dashboard") return <DashboardPreview />;
  if (tab === "customer") return <CustomerPreview />;
  if (tab === "analytics") return <AnalyticsPreview />;
  if (tab === "copilot") return <CopilotPreview />;
  if (tab === "predictions") return <PredictionsPreview />;
  return <ReportsPreview />;
}

function PreviewCard({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={cn("rounded-xl border border-white/[0.08] bg-white/[0.02] p-4", className)}>{children}</div>
  );
}

function DashboardPreview() {
  return (
    <div className="grid h-full grid-cols-4 gap-3">
      {[
        { l: "Revenue", v: "$186M", d: "+8.7%" },
        { l: "Customers", v: "1.24M", d: "+3.2%" },
        { l: "Churn", v: "2.1%", d: "−0.4pt" },
        { l: "NPS", v: "62", d: "+4" },
      ].map((k) => (
        <PreviewCard key={k.l}>
          <div className="text-[10px] uppercase tracking-wider text-white/50">{k.l}</div>
          <div className="mt-1 text-xl font-bold text-white">{k.v}</div>
          <div className="text-[10px] text-emerald-400">{k.d}</div>
        </PreviewCard>
      ))}
      <PreviewCard className="col-span-3 row-span-2">
        <div className="text-xs font-semibold text-white/80">Revenue by segment</div>
        <div className="mt-3 flex h-40 items-end gap-2">
          {[40, 55, 45, 70, 62, 82, 76, 90, 88, 96].map((h, i) => (
            <div key={i} className="flex-1 rounded-t bg-gradient-to-t from-indigo-600 via-violet-500 to-cyan-400" style={{ height: `${h}%` }} />
          ))}
        </div>
      </PreviewCard>
      <PreviewCard className="row-span-2">
        <div className="text-xs font-semibold text-white/80">Top insights</div>
        <ul className="mt-3 space-y-2 text-[11px]">
          {["Churn risk spike · EMEA", "Upsell: 240 accounts", "New cohort: SMB EU"].map((t) => (
            <li key={t} className="flex items-start gap-1.5 text-white/70">
              <ChevronRight className="mt-0.5 h-3 w-3 text-cyan-400" /> {t}
            </li>
          ))}
        </ul>
      </PreviewCard>
    </div>
  );
}

function CustomerPreview() {
  return (
    <div className="grid h-full grid-cols-3 gap-3">
      <PreviewCard>
        <div className="h-12 w-12 rounded-full bg-brand-gradient" />
        <div className="mt-3 text-sm font-semibold text-white">Northwind Financial</div>
        <div className="text-[11px] text-white/50">Enterprise · London · Since 2019</div>
        <div className="mt-4 grid grid-cols-2 gap-2 text-[10px]">
          <div className="rounded-lg bg-white/[0.03] p-2"><div className="text-white/50">LTV</div><div className="text-sm font-bold text-white">$1.4M</div></div>
          <div className="rounded-lg bg-white/[0.03] p-2"><div className="text-white/50">Risk</div><div className="text-sm font-bold text-amber-400">Med</div></div>
        </div>
      </PreviewCard>
      <PreviewCard className="col-span-2">
        <div className="text-xs font-semibold text-white/80">Purchase history</div>
        <svg viewBox="0 0 300 100" className="mt-3 h-24 w-full">
          <defs>
            <linearGradient id="ph" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#6366F1" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#6366F1" stopOpacity="0" />
            </linearGradient>
          </defs>
          <path d="M0,80 L30,65 L60,72 L90,55 L120,60 L150,40 L180,45 L210,25 L240,30 L270,18 L300,22 L300,100 L0,100 Z" fill="url(#ph)" />
          <path d="M0,80 L30,65 L60,72 L90,55 L120,60 L150,40 L180,45 L210,25 L240,30 L270,18 L300,22" fill="none" stroke="#22D3EE" strokeWidth="1.5" />
        </svg>
      </PreviewCard>
      <PreviewCard className="col-span-3">
        <div className="text-xs font-semibold text-white/80">Timeline</div>
        <div className="mt-3 flex gap-3 overflow-hidden">
          {["Contract renewed", "Support ticket", "Upsell added", "QBR completed", "New user activated"].map((e, i) => (
            <div key={e} className="flex-1 rounded-lg border border-white/[0.06] bg-white/[0.02] p-2 text-[10px]">
              <div className="text-white/50">Day {i + 1}</div>
              <div className="mt-0.5 text-white/85">{e}</div>
            </div>
          ))}
        </div>
      </PreviewCard>
    </div>
  );
}

function AnalyticsPreview() {
  return (
    <div className="grid h-full grid-cols-2 gap-3">
      <PreviewCard>
        <div className="text-xs font-semibold text-white/80">Cohort retention</div>
        <div className="mt-3 grid grid-cols-8 gap-1">
          {Array.from({ length: 32 }).map((_, i) => {
            const o = 0.15 + Math.random() * 0.8;
            return <div key={i} className="aspect-square rounded" style={{ background: `rgba(99,102,241,${o.toFixed(2)})` }} />;
          })}
        </div>
      </PreviewCard>
      <PreviewCard>
        <div className="text-xs font-semibold text-white/80">Conversion funnel</div>
        <div className="mt-3 space-y-2">
          {[100, 74, 52, 31, 18].map((w, i) => (
            <div key={i} className="h-6 rounded" style={{ width: `${w}%`, background: "linear-gradient(90deg,#6366F1,#22D3EE)", opacity: 0.9 - i * 0.1 }} />
          ))}
        </div>
      </PreviewCard>
      <PreviewCard className="col-span-2">
        <div className="text-xs font-semibold text-white/80">Revenue by region</div>
        <div className="mt-3 flex h-24 items-end gap-1">
          {Array.from({ length: 40 }).map((_, i) => (
            <div key={i} className="flex-1 rounded-t bg-gradient-to-t from-violet-600 to-cyan-400" style={{ height: `${20 + Math.random() * 80}%` }} />
          ))}
        </div>
      </PreviewCard>
    </div>
  );
}

function CopilotPreview() {
  return (
    <div className="grid h-full grid-cols-4 gap-3">
      <PreviewCard>
        <div className="text-[10px] uppercase tracking-wider text-white/50">Chats</div>
        <ul className="mt-2 space-y-1.5 text-[11px] text-white/70">
          {["Q4 revenue drivers", "EMEA churn cohorts", "Top accounts brief", "SMB expansion"].map((c, i) => (
            <li key={c} className={cn("truncate rounded-md px-2 py-1.5", i === 0 && "bg-white/[0.06] text-white")}>{c}</li>
          ))}
        </ul>
      </PreviewCard>
      <PreviewCard className="col-span-3 flex flex-col">
        <div className="flex-1 space-y-3 overflow-hidden text-[12px]">
          <div className="ml-auto max-w-[70%] rounded-xl rounded-tr-sm bg-white/[0.06] p-3 text-white/90">What drove Q4 revenue growth in Premium?</div>
          <div className="max-w-[85%] rounded-xl rounded-tl-sm bg-brand-gradient/20 p-3 text-white/90 ring-1 ring-white/10">
            Premium revenue grew <span className="text-cyan-300 font-semibold">15.2%</span> MoM, driven mostly by EMEA plan upgrades. 62% of the lift came from 240 accounts on legacy plans.
            <div className="mt-2 text-[10px] text-white/50">Sources · 4 · Confidence 94%</div>
          </div>
        </div>
        <div className="mt-3 flex items-center gap-2 rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-[11px] text-white/50">
          <MessageSquare className="h-3.5 w-3.5" /> Ask a question about your customers…
        </div>
      </PreviewCard>
    </div>
  );
}

function PredictionsPreview() {
  const feats = [
    { n: "Days since login", v: 82 },
    { n: "Support tickets 30d", v: 68 },
    { n: "Contract renewal", v: 54 },
    { n: "Discount ratio", v: 42 },
    { n: "Feature adoption", v: 30 },
  ];
  return (
    <div className="grid h-full grid-cols-3 gap-3">
      <PreviewCard>
        <div className="text-[10px] uppercase tracking-wider text-white/50">Churn probability</div>
        <div className="mt-2 text-4xl font-bold text-white">73%</div>
        <div className="text-[11px] text-amber-400">High risk · 30-day window</div>
        <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/[0.06]">
          <div className="h-full rounded-full bg-gradient-to-r from-amber-500 to-red-500" style={{ width: "73%" }} />
        </div>
      </PreviewCard>
      <PreviewCard className="col-span-2">
        <div className="text-xs font-semibold text-white/80">Feature importance</div>
        <div className="mt-3 space-y-2">
          {feats.map((f) => (
            <div key={f.n} className="flex items-center gap-3 text-[11px] text-white/70">
              <div className="w-32 shrink-0">{f.n}</div>
              <div className="h-2 flex-1 overflow-hidden rounded-full bg-white/[0.06]">
                <div className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-cyan-400" style={{ width: `${f.v}%` }} />
              </div>
              <div className="w-8 text-right text-white/50">{f.v}</div>
            </div>
          ))}
        </div>
      </PreviewCard>
    </div>
  );
}

function ReportsPreview() {
  return (
    <div className="grid h-full grid-cols-3 gap-3">
      {["Executive Brief", "Churn Report", "Revenue by Segment", "Cohort Analysis", "Product Adoption", "Customer Health"].map((r, i) => (
        <PreviewCard key={r} className="flex flex-col justify-between">
          <div>
            <div className="text-[10px] uppercase tracking-wider text-white/50">Report</div>
            <div className="mt-1 text-sm font-semibold text-white">{r}</div>
          </div>
          <div className="mt-3 flex items-center justify-between text-[10px] text-white/50">
            <span>Updated {i + 1}h ago</span>
            <span className="rounded bg-white/[0.06] px-1.5 py-0.5">PDF</span>
          </div>
        </PreviewCard>
      ))}
    </div>
  );
}

// ---------------- Workflow ----------------

function WorkflowSection() {
  return (
    <Section eyebrow="Workflow" title="From raw data to business decision" desc="A transparent journey every stakeholder can inspect and trust.">
      <div className="relative mx-auto mt-14 max-w-4xl">
        <div className="absolute left-8 top-0 h-full w-px bg-gradient-to-b from-transparent via-white/15 to-transparent md:left-1/2" />
        <ol className="space-y-8">
          {WORKFLOW.map((s, i) => (
            <motion.li
              key={s.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.45, delay: i * 0.05 }}
              className={cn(
                "relative flex flex-col gap-4 md:flex-row md:items-center",
                i % 2 === 1 && "md:flex-row-reverse",
              )}
            >
              <div className="md:w-1/2 md:px-8">
                <div className={cn("group rounded-2xl border border-white/[0.08] bg-white/[0.02] p-5 backdrop-blur transition-all hover:border-white/20 hover:bg-white/[0.04]")}>
                  <div className="text-[10px] font-semibold uppercase tracking-[0.24em] text-brand-gradient">
                    Step {String(i + 1).padStart(2, "0")}
                  </div>
                  <div className="mt-1 text-lg font-semibold text-white">{s.title}</div>
                  <div className="mt-1 text-sm text-white/60">{s.desc}</div>
                </div>
              </div>
              {/* Node */}
              <div className="absolute left-8 top-4 md:left-1/2 md:top-1/2 md:-translate-x-1/2 md:-translate-y-1/2">
                <div className="relative">
                  <div className="absolute inset-0 rounded-full bg-brand-gradient blur-md opacity-70" />
                  <div className="relative flex h-4 w-4 items-center justify-center rounded-full bg-brand-gradient ring-4 ring-[#090B14]" />
                </div>
              </div>
              <div className="hidden md:block md:w-1/2" />
            </motion.li>
          ))}
        </ol>
      </div>
    </Section>
  );
}

// ---------------- Features ----------------

function FeaturesSection() {
  return (
    <Section id="solutions" eyebrow="Capabilities" title="Everything you need to understand customers" desc="Modular building blocks that snap into your existing stack.">
      <div className="mt-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {FEATURES.map((f, i) => (
          <motion.div
            key={f.title}
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-60px" }}
            transition={{ duration: 0.4, delay: i * 0.05 }}
          >
            <div className="group relative h-full overflow-hidden rounded-2xl p-[1px] transition-all hover:-translate-y-1">
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-white/10 via-white/[0.02] to-white/10 opacity-70 transition-opacity group-hover:opacity-100" />
              <div className="absolute inset-0 rounded-2xl bg-brand-gradient opacity-0 blur-xl transition-opacity group-hover:opacity-40" />
              <div className="relative h-full rounded-2xl bg-[#0B0E1A] p-6">
                <motion.div
                  whileHover={{ rotate: -6, scale: 1.05 }}
                  className="inline-flex rounded-xl bg-brand-gradient p-2.5 text-white shadow-elegant"
                >
                  <f.icon className="h-5 w-5" />
                </motion.div>
                <h3 className="mt-4 text-base font-semibold text-white">{f.title}</h3>
                <p className="mt-1 text-sm text-white/60">{f.desc}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </Section>
  );
}

// ---------------- Business Impact ----------------

function BusinessImpactSection() {
  return (
    <Section id="resources" eyebrow="Business Impact" title="Before &amp; after CustomerLens" desc="Real changes teams see once customer data becomes decisions.">
      <div className="mt-14 grid gap-6 lg:grid-cols-2">
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="rounded-2xl border border-white/[0.08] bg-white/[0.02] p-8"
        >
          <div className="text-[10px] font-semibold uppercase tracking-[0.24em] text-white/50">Before</div>
          <div className="mt-1 text-xl font-semibold text-white/85">Data scattered, decisions delayed</div>
          <ul className="mt-6 space-y-3">
            {[
              "Scattered spreadsheets across every team",
              "Manual reporting cycles that take weeks",
              "Insights arrive after the opportunity has passed",
              "Poor visibility into churn and revenue signals",
            ].map((t) => (
              <li key={t} className="flex items-start gap-3 text-sm text-white/60">
                <Minus className="mt-0.5 h-4 w-4 shrink-0 text-red-400" /> {t}
              </li>
            ))}
          </ul>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, x: 30 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-indigo-950/60 via-violet-950/40 to-cyan-950/40 p-8"
        >
          <div className="absolute inset-0 opacity-40" style={{ backgroundImage: "radial-gradient(circle at 80% 20%, rgba(139,92,246,0.25), transparent 50%)" }} />
          <div className="relative">
            <div className="text-[10px] font-semibold uppercase tracking-[0.24em] text-brand-gradient">After</div>
            <div className="mt-1 text-xl font-semibold text-white">Unified, predictive, decision-ready</div>
            <div className="mt-6 grid grid-cols-2 gap-4">
              {[
                { k: "+42%", v: "Faster reporting" },
                { k: "-31%", v: "Customer churn" },
                { k: "+18%", v: "Revenue growth" },
                { k: "2x", v: "Faster decisions" },
              ].map((m) => (
                <div key={m.v} className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
                  <div className="text-2xl font-bold text-brand-gradient">{m.k}</div>
                  <div className="mt-1 text-xs text-white/70">{m.v}</div>
                </div>
              ))}
            </div>
            <ul className="mt-6 space-y-2">
              {["Single source of truth for every customer", "Predictive signals delivered in seconds", "Executive briefs generated on demand"].map((t) => (
                <li key={t} className="flex items-start gap-3 text-sm text-white/75">
                  <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" /> {t}
                </li>
              ))}
            </ul>
          </div>
        </motion.div>
      </div>
    </Section>
  );
}

// ---------------- Metrics ----------------

function MetricsSection() {
  return (
    <section id="industries" className="scroll-mt-20">
      <div className="mx-auto max-w-7xl px-6 py-24">
        <div className="rounded-3xl border border-white/[0.08] bg-white/[0.02] p-10 backdrop-blur">
          <div className="grid gap-6 md:grid-cols-5">
            {METRICS.map((m, i) => (
              <motion.div
                key={m.label}
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.05 }}
                className="text-center"
              >
                <div className="text-3xl font-bold text-brand-gradient md:text-4xl">
                  {m.prefix ?? ""}
                  <AnimatedNumber value={m.value} decimals={0} />
                  {m.suffix ?? ""}
                </div>
                <div className="mt-1 text-xs uppercase tracking-wider text-white/60">{m.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

// ---------------- Security ----------------

function SecuritySection() {
  return (
    <section id="pricing" className="relative scroll-mt-20 overflow-hidden py-24 md:py-32">
      <div className="mx-auto grid max-w-7xl gap-12 px-6 lg:grid-cols-2 lg:items-center">
        <div>
          <div className="text-[10px] font-semibold uppercase tracking-[0.24em] text-brand-gradient">Security</div>
          <h2 className="mt-2 text-3xl font-semibold tracking-tight text-white md:text-4xl">
            Enterprise-grade security, built in
          </h2>
          <p className="mt-4 max-w-lg text-white/60">
            Encryption, granular access controls, and full auditability. Deploy on shared, single-tenant,
            or fully private infrastructure.
          </p>
          <div className="mt-8 grid gap-3 sm:grid-cols-2">
            {SECURITY.map((s) => (
              <div key={s.t} className="flex items-center gap-3 rounded-xl border border-white/[0.08] bg-white/[0.02] p-4">
                <div className="rounded-lg bg-brand-gradient/20 p-2 ring-1 ring-white/10">
                  <s.icon className="h-4 w-4 text-brand-gradient" />
                </div>
                <div className="text-sm font-medium text-white">{s.t}</div>
              </div>
            ))}
          </div>
        </div>
        <div className="relative flex items-center justify-center">
          <ShieldIllustration />
        </div>
      </div>
    </section>
  );
}

function ShieldIllustration() {
  return (
    <div className="relative h-[380px] w-full max-w-md">
      <div className="absolute inset-0 rounded-full bg-brand-gradient opacity-25 blur-3xl" />
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          className="absolute inset-0 rounded-full border border-white/10"
          style={{ margin: `${i * 30}px` }}
          animate={{ scale: [1, 1.05, 1], opacity: [0.4, 0.7, 0.4] }}
          transition={{ duration: 3 + i * 0.5, repeat: Infinity, delay: i * 0.4 }}
        />
      ))}
      <div className="absolute inset-0 flex items-center justify-center">
        <motion.div
          animate={{ y: [-4, 4, -4] }}
          transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
          className="relative"
        >
          <div className="absolute inset-0 rounded-3xl bg-brand-gradient blur-2xl opacity-60" />
          <div className="relative flex h-40 w-40 items-center justify-center rounded-3xl bg-gradient-to-br from-indigo-600 via-violet-600 to-cyan-500 shadow-2xl">
            <ShieldCheck className="h-20 w-20 text-white" strokeWidth={1.5} />
          </div>
        </motion.div>
      </div>
    </div>
  );
}

// ---------------- Final CTA ----------------

function FinalCTA({ onDemoOpen }: { onDemoOpen: () => void }) {
  return (
    <section id="company" className="scroll-mt-20 px-6 pb-24">
      <div className="relative mx-auto max-w-6xl overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-indigo-950 via-violet-950 to-[#090B14] p-10 md:p-16">
        <motion.div
          animate={{ backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"] }}
          transition={{ duration: 12, repeat: Infinity, ease: "linear" }}
          className="absolute inset-0 opacity-40"
          style={{
            backgroundImage: "linear-gradient(120deg, rgba(99,102,241,0.4), rgba(139,92,246,0.4), rgba(34,211,238,0.4), rgba(99,102,241,0.4))",
            backgroundSize: "300% 300%",
          }}
        />
        <div className="pointer-events-none absolute inset-0 opacity-[0.08] [background-image:radial-gradient(circle_at_1px_1px,white_1px,transparent_0)] [background-size:24px_24px]" />

        <div className="relative text-center">
          <h2 className="text-3xl font-semibold tracking-tight text-white md:text-5xl">
            Ready to Understand Every Customer?
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-white/70">
            Transform customer data into meaningful business intelligence with CustomerLens.
          </p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
            <Button
              onClick={onDemoOpen}
              size="lg"
              className="h-12 gap-2 bg-white px-6 text-indigo-700 shadow-elegant hover:bg-white/90"
            >
              Book Demo <ArrowRight className="h-4 w-4" />
            </Button>
            <a href="#platform">
              <Button
                size="lg"
                variant="outline"
                className="h-12 gap-2 border-white/20 bg-white/[0.04] text-white hover:bg-white/10"
              >
                Explore Platform
              </Button>
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}

// ---------------- Footer ----------------

function Footer() {
  return (
    <footer className="border-t border-white/[0.06] bg-[#070912]">
      <div className="mx-auto max-w-7xl px-6 py-16">
        <div className="grid gap-10 md:grid-cols-5">
          <div className="md:col-span-2">
            <Logo />
            <p className="mt-4 max-w-sm text-sm text-white/55">
              CustomerLens is the enterprise customer intelligence platform that turns data into decisions.
            </p>
            <div className="mt-6 flex items-center gap-3">
              {[
                { i: Github, l: "GitHub" },
                { i: Linkedin, l: "LinkedIn" },
                { i: Twitter, l: "Twitter" },
                { i: Mail, l: "Contact" },
              ].map((s) => (
                <a key={s.l} href="#" aria-label={s.l} className="rounded-lg border border-white/10 bg-white/[0.02] p-2 text-white/60 transition hover:bg-white/[0.06] hover:text-white">
                  <s.i className="h-4 w-4" />
                </a>
              ))}
            </div>
          </div>
          {[
            { h: "Product", items: ["Platform", "Solutions", "Documentation", "API"] },
            { h: "Company", items: ["Pricing", "Security", "Privacy", "Terms"] },
            { h: "Resources", items: ["GitHub", "LinkedIn", "Contact", "Careers"] },
          ].map((col) => (
            <div key={col.h}>
              <div className="text-xs font-semibold uppercase tracking-wider text-white/50">{col.h}</div>
              <ul className="mt-4 space-y-2">
                {col.items.map((i) => (
                  <li key={i}>
                    <a href="#" className="text-sm text-white/70 transition hover:text-white">
                      {i}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 flex flex-col items-start justify-between gap-6 border-t border-white/[0.06] pt-8 md:flex-row md:items-center">
          <div className="text-xs text-white/40">
            © {new Date().getFullYear()} CustomerLens, Inc. All rights reserved.
          </div>
          <form
            onSubmit={(e) => e.preventDefault()}
            className="flex w-full max-w-sm items-center gap-2"
          >
            <input
              type="email"
              placeholder="Newsletter · work email"
              className="h-10 flex-1 rounded-lg border border-white/10 bg-white/[0.02] px-3 text-sm text-white placeholder:text-white/40 focus:border-white/25 focus:outline-none"
            />
            <Button className="h-10 bg-brand-gradient px-4 text-primary-foreground hover:opacity-95">
              Subscribe <ArrowUpRight className="ml-1 h-3.5 w-3.5" />
            </Button>
          </form>
        </div>
      </div>
    </footer>
  );
}

// ---------------- Helpers ----------------

function Section({
  id,
  eyebrow,
  title,
  desc,
  children,
}: {
  id?: string;
  eyebrow: string;
  title: string;
  desc?: string;
  children: React.ReactNode;
}) {
  return (
    <section id={id} className="mx-auto max-w-7xl scroll-mt-20 px-6 py-24 md:py-32">
      <SectionHeader eyebrow={eyebrow} title={title} desc={desc} />
      {children}
    </section>
  );
}

function SectionHeader({ eyebrow, title, desc }: { eyebrow: string; title: string; desc?: string }) {
  return (
    <div className="mx-auto max-w-3xl text-center">
      <div className="text-[10px] font-semibold uppercase tracking-[0.28em] text-brand-gradient">
        {eyebrow}
      </div>
      <h2 className="mt-3 text-3xl font-semibold tracking-tight text-white md:text-5xl">
        {title}
      </h2>
      {desc && <p className="mx-auto mt-4 max-w-2xl text-white/60">{desc}</p>}
    </div>
  );
}
