import { createFileRoute, Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { useMemo, useState } from "react";
import { ArrowRight, Check, Minus, Sparkles, Building2, Rocket, Shield } from "lucide-react";
import { Logo } from "@/components/brand/Logo";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { DemoModal } from "@/components/landing/DemoModal";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/pricing")({
  head: () => ({
    meta: [
      { title: "Pricing — CustomerLens" },
      {
        name: "description",
        content:
          "Choose the CustomerLens plan that fits your team — Starter, Growth, or Enterprise. Transparent pricing with a full feature comparison and enterprise-grade security.",
      },
      { property: "og:title", content: "Pricing — CustomerLens" },
      {
        property: "og:description",
        content:
          "Transparent plans for teams turning customer data into business growth. Compare Starter, Growth, and Enterprise side by side.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: PricingPage,
});

type BillingCycle = "monthly" | "annual";

type Tier = {
  id: "starter" | "growth" | "enterprise";
  name: string;
  icon: typeof Rocket;
  tagline: string;
  monthly: number | null;
  annual: number | null;
  priceSuffix: string;
  highlights: string[];
  featured?: boolean;
  cta: string;
};

const TIERS: Tier[] = [
  {
    id: "starter",
    name: "Starter",
    icon: Rocket,
    tagline: "For small teams getting started with customer intelligence.",
    monthly: 49,
    annual: 39,
    priceSuffix: "per user / month",
    highlights: [
      "Up to 25,000 customer records",
      "3 connected data sources",
      "Customer 360 & basic analytics",
      "Standard dashboards & reports",
      "Email support",
    ],
    cta: "Book a Live Demo",
  },
  {
    id: "growth",
    name: "Growth",
    icon: Sparkles,
    tagline: "For growing companies scaling customer operations.",
    monthly: 149,
    annual: 119,
    priceSuffix: "per user / month",
    featured: true,
    highlights: [
      "Up to 500,000 customer records",
      "15 connected data sources",
      "Predictive analytics & churn scoring",
      "AI Copilot & document intelligence",
      "Custom dashboards & scheduled reports",
      "Priority support with SLA",
    ],
    cta: "Book a Live Demo",
  },
  {
    id: "enterprise",
    name: "Enterprise",
    icon: Building2,
    tagline: "For regulated organizations with advanced security needs.",
    monthly: null,
    annual: null,
    priceSuffix: "custom pricing",
    highlights: [
      "Unlimited records & sources",
      "Private deployment (VPC / on-prem)",
      "SSO, SCIM, granular RBAC",
      "Dedicated success & solutions team",
      "Custom models & fine-tuning",
      "24/7 enterprise support",
    ],
    cta: "Talk to Sales",
  },
];

type FeatureRow = { label: string; values: [ValueCell, ValueCell, ValueCell] };
type ValueCell = boolean | string;

const FEATURE_GROUPS: { group: string; rows: FeatureRow[] }[] = [
  {
    group: "Platform",
    rows: [
      { label: "Customer records", values: ["25K", "500K", "Unlimited"] },
      { label: "Connected data sources", values: ["3", "15", "Unlimited"] },
      { label: "Team seats", values: ["Up to 10", "Up to 50", "Unlimited"] },
      { label: "Dashboards", values: [true, true, true] },
      { label: "Custom dashboards", values: [false, true, true] },
    ],
  },
  {
    group: "Intelligence",
    rows: [
      { label: "Customer 360 profiles", values: [true, true, true] },
      { label: "AI Copilot", values: [false, true, true] },
      { label: "Predictive analytics & churn", values: [false, true, true] },
      { label: "Document & knowledge search", values: [false, true, true] },
      { label: "Custom models & fine-tuning", values: [false, false, true] },
    ],
  },
  {
    group: "Security & governance",
    rows: [
      { label: "SOC 2 · GDPR", values: [true, true, true] },
      { label: "Role-based access control", values: [true, true, true] },
      { label: "SSO / SAML", values: [false, true, true] },
      { label: "SCIM provisioning", values: [false, false, true] },
      { label: "Private deployment (VPC / on-prem)", values: [false, false, true] },
      { label: "Audit logs & data residency", values: [false, true, true] },
    ],
  },
  {
    group: "Support",
    rows: [
      { label: "Email support", values: [true, true, true] },
      { label: "Priority support with SLA", values: [false, true, true] },
      { label: "Dedicated success manager", values: [false, false, true] },
      { label: "24/7 enterprise support", values: [false, false, true] },
    ],
  },
];

const FAQ = [
  {
    q: "Can I change plans later?",
    a: "Yes — upgrade or downgrade at any time. Annual plans are prorated automatically.",
  },
  {
    q: "Is there a free trial?",
    a: "Book a live demo and our team will set up a tailored sandbox with your sample data.",
  },
  {
    q: "How does Enterprise pricing work?",
    a: "Enterprise is priced by usage, deployment model, and support tier. Talk to sales for a quote.",
  },
  {
    q: "Do you offer discounts for startups or nonprofits?",
    a: "Yes — qualified startups and nonprofit organizations receive up to 40% off Growth plans.",
  },
];

function PricingPage() {
  const [demoOpen, setDemoOpen] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<string | undefined>();
  const [cycle, setCycle] = useState<BillingCycle>("annual");

  const openDemo = (plan?: string) => {
    setSelectedPlan(plan);
    setDemoOpen(true);
  };

  const savings = useMemo(() => (cycle === "annual" ? "Save ~20%" : "Billed monthly"), [cycle]);

  return (
    <div className="min-h-screen bg-[#090B14] text-white">
      {/* Ambient background */}
      <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute -top-40 left-1/2 h-[520px] w-[720px] -translate-x-1/2 rounded-full bg-brand-gradient opacity-[0.12] blur-[120px]" />
        <div className="absolute bottom-0 right-0 h-[420px] w-[420px] rounded-full bg-brand-gradient opacity-[0.08] blur-[120px]" />
      </div>

      {/* Header */}
      <header className="sticky top-0 z-40 border-b border-white/[0.06] bg-[#090B14]/70 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
          <Link to="/" className="flex items-center">
            <Logo />
          </Link>
          <nav className="hidden items-center gap-1 lg:flex">
            {[
              { label: "Platform", href: "/#platform" },
              { label: "Solutions", href: "/#solutions" },
              { label: "Industries", href: "/#industries" },
              { label: "Resources", href: "/#resources" },
            ].map((n) => (
              <a
                key={n.label}
                href={n.href}
                className="rounded-md px-3 py-2 text-sm text-white/70 transition hover:bg-white/5 hover:text-white"
              >
                {n.label}
              </a>
            ))}
            <span className="rounded-md px-3 py-2 text-sm text-white">Pricing</span>
          </nav>
          <div className="flex items-center gap-2">
            <Link
              to="/login"
              className="hidden rounded-md px-3 py-2 text-sm font-medium text-white/80 transition hover:text-white sm:inline-flex"
            >
              Sign In
            </Link>
            <Button
              onClick={() => openDemo()}
              size="sm"
              className="h-9 gap-1.5 bg-brand-gradient px-4 text-primary-foreground shadow-elegant hover:opacity-95"
            >
              Book Demo <ArrowRight className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="mx-auto max-w-7xl px-6 pt-20 pb-10 text-center md:pt-28">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] px-3 py-1 text-xs text-white/70">
            <Shield className="h-3.5 w-3.5" /> Transparent enterprise pricing
          </div>
          <h1 className="mt-5 text-4xl font-bold tracking-tight md:text-6xl">
            Plans that scale with your{" "}
            <span className="bg-brand-gradient bg-clip-text text-transparent">customer intelligence</span>
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-lg text-white/70">
            Start small, grow into predictive analytics, or deploy privately across the enterprise.
            Every plan includes SOC 2, GDPR, and role-based access.
          </p>
        </motion.div>

        {/* Billing toggle */}
        <div className="mt-10 flex items-center justify-center gap-3">
          <div className="inline-flex items-center rounded-full border border-white/10 bg-white/[0.03] p-1">
            {(["monthly", "annual"] as BillingCycle[]).map((c) => (
              <button
                key={c}
                onClick={() => setCycle(c)}
                className={cn(
                  "relative rounded-full px-5 py-2 text-sm font-medium capitalize transition",
                  cycle === c ? "text-white" : "text-white/60 hover:text-white",
                )}
              >
                {cycle === c && (
                  <motion.span
                    layoutId="cycle-pill"
                    className="absolute inset-0 rounded-full bg-brand-gradient shadow-elegant"
                    transition={{ type: "spring", damping: 24, stiffness: 260 }}
                  />
                )}
                <span className="relative">{c}</span>
              </button>
            ))}
          </div>
          <span className="text-xs text-white/50">{savings}</span>
        </div>
      </section>

      {/* Tier cards */}
      <section className="mx-auto max-w-7xl px-6 pb-16">
        <div className="grid gap-6 md:grid-cols-3">
          {TIERS.map((t, i) => (
            <motion.div
              key={t.id}
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: i * 0.08 }}
              className="relative"
            >
              {t.featured && (
                <div className="absolute -inset-px rounded-2xl bg-brand-gradient opacity-70 blur-[2px]" />
              )}
              <Card
                className={cn(
                  "relative flex h-full flex-col overflow-hidden rounded-2xl border-white/10 bg-[#0B0E1A] p-7 shadow-elegant",
                  t.featured && "border-transparent",
                )}
              >
                {t.featured && (
                  <div className="absolute right-5 top-5 rounded-full bg-brand-gradient px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-white">
                    Most popular
                  </div>
                )}
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white/5 ring-1 ring-white/10">
                    <t.icon className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold">{t.name}</h3>
                  </div>
                </div>
                <p className="mt-3 text-sm text-white/60">{t.tagline}</p>

                <div className="mt-6 flex items-end gap-2">
                  {t.monthly !== null ? (
                    <>
                      <span className="text-5xl font-bold tracking-tight">
                        ${cycle === "annual" ? t.annual : t.monthly}
                      </span>
                      <span className="pb-2 text-sm text-white/60">/mo</span>
                    </>
                  ) : (
                    <span className="text-4xl font-bold tracking-tight">Custom</span>
                  )}
                </div>
                <div className="mt-1 text-xs text-white/50">{t.priceSuffix}</div>

                <Button
                  onClick={() => openDemo(t.name)}
                  className={cn(
                    "mt-6 h-11 w-full gap-1.5",
                    t.featured
                      ? "bg-brand-gradient text-primary-foreground shadow-elegant hover:opacity-95"
                      : "border border-white/15 bg-white/5 text-white hover:bg-white/10",
                  )}
                >
                  {t.cta} <ArrowRight className="h-4 w-4" />
                </Button>

                <div className="mt-7 h-px w-full bg-white/[0.06]" />
                <ul className="mt-5 space-y-3">
                  {t.highlights.map((h) => (
                    <li key={h} className="flex items-start gap-2.5 text-sm text-white/80">
                      <Check className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />
                      <span>{h}</span>
                    </li>
                  ))}
                </ul>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Comparison table */}
      <section className="mx-auto max-w-7xl px-6 pb-16">
        <div className="mb-8 text-center">
          <h2 className="text-3xl font-bold tracking-tight md:text-4xl">Compare every feature</h2>
          <p className="mt-3 text-white/60">A side-by-side look at what's in each plan.</p>
        </div>

        <div className="overflow-hidden rounded-2xl border border-white/10 bg-[#0B0E1A]/60">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[720px] text-left text-sm">
              <thead className="sticky top-0 bg-[#0B0E1A]">
                <tr className="border-b border-white/10">
                  <th className="w-[38%] px-6 py-5 text-xs font-semibold uppercase tracking-wider text-white/50">
                    Features
                  </th>
                  {TIERS.map((t) => (
                    <th key={t.id} className="px-6 py-5 text-center">
                      <div className="text-sm font-semibold text-white">{t.name}</div>
                      <div className="mt-0.5 text-xs text-white/50">
                        {t.monthly !== null ? `$${cycle === "annual" ? t.annual : t.monthly}/mo` : "Custom"}
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {FEATURE_GROUPS.map((g) => (
                  <FeatureGroupRows key={g.group} group={g} />
                ))}
                <tr className="border-t border-white/10 bg-white/[0.02]">
                  <td className="px-6 py-5" />
                  {TIERS.map((t) => (
                    <td key={t.id} className="px-6 py-5 text-center">
                      <Button
                        onClick={() => openDemo(t.name)}
                        size="sm"
                        className={cn(
                          "h-9 gap-1.5",
                          t.featured
                            ? "bg-brand-gradient text-primary-foreground shadow-elegant hover:opacity-95"
                            : "border border-white/15 bg-white/5 text-white hover:bg-white/10",
                        )}
                      >
                        {t.cta}
                      </Button>
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="mx-auto max-w-4xl px-6 pb-24">
        <div className="mb-8 text-center">
          <h2 className="text-3xl font-bold tracking-tight md:text-4xl">Pricing questions</h2>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          {FAQ.map((f) => (
            <Card key={f.q} className="rounded-xl border-white/10 bg-[#0B0E1A] p-5">
              <div className="text-sm font-semibold text-white">{f.q}</div>
              <div className="mt-2 text-sm text-white/65">{f.a}</div>
            </Card>
          ))}
        </div>
      </section>

      {/* Final CTA */}
      <section className="mx-auto max-w-7xl px-6 pb-24">
        <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-[#0B0E1A] p-10 text-center md:p-14">
          <div className="absolute inset-0 bg-brand-gradient opacity-[0.10]" />
          <div className="pointer-events-none absolute -top-24 left-1/2 h-72 w-[520px] -translate-x-1/2 rounded-full bg-brand-gradient opacity-40 blur-3xl" />
          <div className="relative">
            <h3 className="text-3xl font-bold tracking-tight md:text-4xl">
              Ready to understand every customer?
            </h3>
            <p className="mx-auto mt-3 max-w-2xl text-white/70">
              Book a personalized walkthrough and we'll tailor the plan to your team, data, and goals.
            </p>
            <div className="mt-7 flex flex-wrap items-center justify-center gap-3">
              <Button
                onClick={() => openDemo()}
                className="h-12 gap-1.5 bg-brand-gradient px-6 text-primary-foreground shadow-elegant hover:opacity-95"
              >
                Book a Live Demo <ArrowRight className="h-4 w-4" />
              </Button>
              <Link
                to="/"
                className="inline-flex h-12 items-center justify-center rounded-md border border-white/15 bg-white/5 px-6 text-sm font-medium text-white transition hover:bg-white/10"
              >
                Explore Platform
              </Link>
            </div>
          </div>
        </div>
      </section>

      <DemoModal open={demoOpen} onClose={() => setDemoOpen(false)} plan={selectedPlan} />
    </div>
  );
}

function FeatureGroupRows({ group }: { group: (typeof FEATURE_GROUPS)[number] }) {
  return (
    <>
      <tr className="bg-white/[0.02]">
        <td
          colSpan={4}
          className="px-6 py-3 text-xs font-semibold uppercase tracking-wider text-brand-gradient"
        >
          {group.group}
        </td>
      </tr>
      {group.rows.map((row) => (
        <tr key={row.label} className="border-t border-white/[0.06] transition hover:bg-white/[0.02]">
          <td className="px-6 py-4 text-white/85">{row.label}</td>
          {row.values.map((v, idx) => (
            <td key={idx} className="px-6 py-4 text-center">
              {typeof v === "boolean" ? (
                v ? (
                  <Check className="mx-auto h-4 w-4 text-emerald-400" />
                ) : (
                  <Minus className="mx-auto h-4 w-4 text-white/25" />
                )
              ) : (
                <span className="text-white/85">{v}</span>
              )}
            </td>
          ))}
        </tr>
      ))}
    </>
  );
}
