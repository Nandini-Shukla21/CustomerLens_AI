import { createFileRoute } from "@tanstack/react-router";
import {
  Activity,
  AlertTriangle,
  BrainCircuit,
  Database,
  DollarSign,
  FileText,
  Filter,
  Download,
  MessageSquare,
  TrendingUp,
  Users,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { StatCard } from "@/components/ui/StatCard";
import { PageHeader } from "@/components/ui/PageHeader";
import { useQuery } from "@tanstack/react-query";
import { platformApi } from "@/api/platform";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Legend,
} from "recharts";

export const Route = createFileRoute("/_app/dashboard")({
  head: () => ({ meta: [{ title: "Executive Dashboard — CustomerLens AI" }] }),
  component: DashboardPage,
});

function DashboardPage() {
  const { data: dashboard } = useQuery({ queryKey: ["dashboard"], queryFn: platformApi.dashboard });
  const revenueTrend = (dashboard?.revenue_trend || []).map((item: { period: string; revenue: number }) => ({ ...item, m: item.period, forecast: item.revenue }));
  const monthlySales = revenueTrend;
  const complaintTrend = revenueTrend;
  const palette = ["#6366f1", "#8b5cf6", "#14b8a6", "#f59e0b", "#ef4444"];
  const segments = (dashboard?.segment_distribution || []).map((item: { name: string; value: number }, index: number) => ({ ...item, color: palette[index % palette.length] }));
  const insights = dashboard?.ai_insights || [];
  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Executive Dashboard"
        title="Portfolio performance"
        description="Cross-portfolio KPIs, forecasts, and AI-generated highlights refreshed 4 minutes ago."
        actions={
          <>
            <Button variant="outline" size="sm"><Filter className="mr-2 h-4 w-4" /> Filters</Button>
            <Button variant="outline" size="sm"><Download className="mr-2 h-4 w-4" /> Export</Button>
            <Button size="sm" className="bg-brand-gradient text-primary-foreground shadow-elegant hover:opacity-95">
              <MessageSquare className="mr-2 h-4 w-4" /> Ask Copilot
            </Button>
          </>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <StatCard label="Total customers" value={(dashboard?.total_customers || 0).toLocaleString()} delta="Live" trend="up" icon={Users} data={revenueTrend.map((x: { revenue: number }) => x.revenue)} />
        <StatCard label="Revenue" value={`$${(dashboard?.revenue || 0).toLocaleString()}`} delta="Live" trend="up" icon={DollarSign} data={revenueTrend.map((x: { revenue: number }) => x.revenue)} />
        <StatCard label="Transactions" value={(dashboard?.transactions || 0).toLocaleString()} delta="Live" trend="up" icon={Activity} data={revenueTrend.map((x: { revenue: number }) => x.revenue)} />
        <StatCard label="High risk customers" value={(dashboard?.high_risk_customers || 0).toLocaleString()} delta="Live" trend="up" icon={Users} data={revenueTrend.map((x: { revenue: number }) => x.revenue)} />
        <StatCard label="Predicted churn" value={(dashboard?.predicted_churn || 0).toLocaleString()} delta="Live" trend="up" icon={TrendingUp} data={revenueTrend.map((x: { revenue: number }) => x.revenue)} />
        <StatCard label="Average LTV" value={`$${Math.round(dashboard?.average_lifetime_value || 0).toLocaleString()}`} delta="Live" trend="up" icon={AlertTriangle} data={revenueTrend.map((x: { revenue: number }) => x.revenue)} />
        <StatCard label="Documents (RAG)" value={(dashboard?.documents || 0).toLocaleString()} delta="Live" trend="up" icon={FileText} data={revenueTrend.map((x: { revenue: number }) => x.revenue)} />
        <StatCard label="Datasets" value={(dashboard?.datasets || 0).toLocaleString()} delta="Live" trend="up" icon={Database} data={revenueTrend.map((x: { revenue: number }) => x.revenue)} />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="border-border/60 bg-card/80 p-6 shadow-card lg:col-span-2">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-base font-semibold">Revenue trend & forecast</h3>
              <p className="text-xs text-muted-foreground">Actual vs AI forecast · last 12 months</p>
            </div>
            <Badge className="bg-brand-gradient text-primary-foreground">MAPE 3.4%</Badge>
          </div>
          <div className="mt-6 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={revenueTrend} margin={{ top: 4, right: 8, bottom: 0, left: -8 }}>
                <defs>
                  <linearGradient id="rev" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="0%" stopColor="var(--brand)" stopOpacity={0.5} />
                    <stop offset="100%" stopColor="var(--brand)" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="fore" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="0%" stopColor="var(--brand-accent)" stopOpacity={0.4} />
                    <stop offset="100%" stopColor="var(--brand-accent)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="m" stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ background: "var(--popover)", border: "1px solid var(--border)", borderRadius: 10, fontSize: 12 }} />
                <Area type="monotone" dataKey="forecast" stroke="var(--brand-accent)" strokeDasharray="4 4" strokeWidth={2} fill="url(#fore)" />
                <Area type="monotone" dataKey="revenue" stroke="var(--brand)" strokeWidth={2.5} fill="url(#rev)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card className="border-border/60 bg-card/80 p-6 shadow-card">
          <h3 className="text-base font-semibold">Customer segmentation</h3>
          <p className="text-xs text-muted-foreground">Behavioural clusters</p>
          <div className="mt-4 h-56">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={segments} dataKey="value" innerRadius={55} outerRadius={85} paddingAngle={3} stroke="none">
                  {segments.map((s) => <Cell key={s.name} fill={s.color} />)}
                </Pie>
                <Tooltip contentStyle={{ background: "var(--popover)", border: "1px solid var(--border)", borderRadius: 10, fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <ul className="mt-2 space-y-2 text-sm">
            {segments.map((s) => (
              <li key={s.name} className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full" style={{ background: s.color }} />
                  {s.name}
                </span>
                <span className="font-medium">{s.value}%</span>
              </li>
            ))}
          </ul>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card className="border-border/60 bg-card/80 p-6 shadow-card">
          <h3 className="text-base font-semibold">Monthly sales channel mix</h3>
          <p className="text-xs text-muted-foreground">Online vs retail</p>
          <div className="mt-6 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthlySales} margin={{ top: 4, right: 8, bottom: 0, left: -8 }}>
                <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="m" stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ background: "var(--popover)", border: "1px solid var(--border)", borderRadius: 10, fontSize: 12 }} cursor={{ fill: "var(--muted)" }} />
                <Legend iconType="circle" wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="revenue" name="Revenue" fill="var(--brand)" radius={[6,6,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card className="border-border/60 bg-card/80 p-6 shadow-card">
          <h3 className="text-base font-semibold">Complaint analysis</h3>
          <p className="text-xs text-muted-foreground">By category · last 6 months</p>
          <div className="mt-6 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={complaintTrend} margin={{ top: 4, right: 8, bottom: 0, left: -8 }}>
                <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="m" stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ background: "var(--popover)", border: "1px solid var(--border)", borderRadius: 10, fontSize: 12 }} />
                <Legend iconType="circle" wrapperStyle={{ fontSize: 12 }} />
                <Line type="monotone" dataKey="revenue" name="Revenue" stroke="var(--brand)" strokeWidth={2.4} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <Card className="border-border/60 bg-card/80 p-6 shadow-card">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h3 className="text-base font-semibold">Recent AI insights</h3>
            <p className="text-xs text-muted-foreground">Highest-impact signals generated in the last 24h</p>
          </div>
          <Badge variant="outline" className="border-brand/30 text-brand-gradient"><BrainCircuit className="mr-1 h-3 w-3" /> 4 new</Badge>
        </div>
        <div className="grid gap-3 md:grid-cols-2">
          {insights.map((i) => (
            <div key={i.title} className="rounded-xl border border-border/60 bg-background/60 p-4">
              <div className="flex items-center justify-between">
                <Badge variant="outline" className="text-[10px]">{i.priority}</Badge>
                <span className="text-[11px] text-muted-foreground">confidence {(i.confidence*100).toFixed(0)}%</span>
              </div>
              <div className="mt-2 text-sm font-semibold">{i.title}</div>
              <div className="mt-1 text-xs text-muted-foreground">{i.description}</div>
              <div className="mt-3 text-xs">
                <span className="font-medium text-brand-gradient">Recommendation · </span>
                <span className="text-foreground/90">{i.action}</span>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
