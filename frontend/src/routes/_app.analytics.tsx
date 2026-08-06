import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/PageHeader";
import { platformApi } from "@/api/platform";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export const Route = createFileRoute("/_app/analytics")({ component: AnalyticsPage });
const colors = ["#6366f1", "#8b5cf6", "#14b8a6", "#f59e0b", "#ef4444"];

function AnalyticsPage() {
  const { data, isLoading, error } = useQuery({ queryKey: ["analytics"], queryFn: () => platformApi.analytics() });
  const trend = (data?.revenue_trend ?? []).map((x: { period: string; revenue: number }) => ({ ...x, label: x.period }));
  const segments = data?.segments ?? [];
  return <div className="space-y-6"><PageHeader eyebrow="Analytics" title="Business analytics" description="Live analysis of your most recently uploaded dataset." />
    {isLoading && <p className="text-sm text-muted-foreground">Loading uploaded dataset analytics…</p>}{error && <p className="text-sm text-destructive">{error.message}</p>}
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{[
      ["Records", data?.records ?? 0], ["Customers", data?.kpis?.total_customers ?? 0], ["Revenue", `$${Number(data?.kpis?.revenue ?? 0).toLocaleString()}`], ["Average LTV", `$${Number(data?.kpis?.average_lifetime_value ?? 0).toLocaleString()}`],
    ].map(([label, value]) => <Card key={String(label)} className="p-5"><div className="text-xs text-muted-foreground">{label}</div><div className="mt-1 text-2xl font-bold">{value}</div></Card>)}</div>
    <div className="grid gap-4 lg:grid-cols-2"><Chart title="Revenue trend"><LineChart data={trend}><Grid/><XAxis dataKey="label"/><YAxis/><Tooltip/><Line dataKey="revenue" stroke="var(--brand)" strokeWidth={2.5}/></LineChart></Chart><Chart title="Revenue over time"><AreaChart data={trend}><Grid/><XAxis dataKey="label"/><YAxis/><Tooltip/><Area dataKey="revenue" stroke="var(--brand)" fill="var(--brand)" fillOpacity={.25}/></AreaChart></Chart><Chart title="Revenue by period"><BarChart data={trend}><Grid/><XAxis dataKey="label"/><YAxis/><Tooltip/><Bar dataKey="revenue" fill="var(--brand)"/></BarChart></Chart>
      <Chart title="Customer segments"><PieChart><Pie data={segments} dataKey="value" nameKey="name" outerRadius={90}>{segments.map((_: unknown, i: number) => <Cell key={i} fill={colors[i % colors.length]}/>)}</Pie><Tooltip/></PieChart></Chart></div>
  </div>;
}
function Grid() { return <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false}/>; }
function Chart({ title, children }: { title: string; children: React.ReactElement }) { return <Card className="p-6"><h3 className="font-semibold">{title}</h3><div className="mt-4 h-64"><ResponsiveContainer width="100%" height="100%">{children}</ResponsiveContainer></div></Card>; }
