import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/PageHeader";
import { platformApi } from "@/api/platform";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Scatter, ScatterChart } from "recharts";

export const Route = createFileRoute("/_app/analytics")({ component: AnalyticsPage });
const colors = ["#6366f1", "#8b5cf6", "#14b8a6", "#f59e0b", "#ef4444"];

function AnalyticsPage() {
  const [selectedDatasetId, setSelectedDatasetId] = useState("");

  const { data: datasets = [] } = useQuery({ queryKey: ["datasets"], queryFn: platformApi.datasets });

  useEffect(() => {
    if (datasets.length > 0 && !selectedDatasetId) {
      setSelectedDatasetId(datasets[0].id);
    }
  }, [datasets, selectedDatasetId]);

  const { data, isLoading, error } = useQuery({
    queryKey: ["analytics", selectedDatasetId],
    queryFn: () => platformApi.analytics(selectedDatasetId || undefined),
    enabled: datasets.length === 0 || Boolean(selectedDatasetId),
  });

  const metrics = data?.metrics ?? data?.kpis ?? {};

  const charts = data?.charts ?? [];
  return (
    <div className="space-y-6">
      <PageHeader eyebrow="Analytics" title="Dataset analytics" description="Explore metrics and charts computed from the selected dataset." />

      <Card className="p-5">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-sm font-semibold">Dataset</h2>
            <p className="text-xs text-muted-foreground">Choose which dataset should power the analytics.</p>
          </div>
          <select
            className="max-w-xs rounded border p-2"
            value={selectedDatasetId}
            onChange={(event) => setSelectedDatasetId(event.target.value)}
          >
            <option value="">Use most recent dataset</option>
            {datasets.map((dataset) => (
              <option key={dataset.id} value={dataset.id}>
                {dataset.filename}
              </option>
            ))}
          </select>
        </div>
      </Card>

      {isLoading && <p className="text-sm text-muted-foreground">Loading uploaded dataset analytics…</p>}
      {error && <p className="text-sm text-destructive">{error.message}</p>}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          ["Records", data?.records ?? metrics?.records?.value ?? 0],
          ["Customers", metrics?.total_customers ? (metrics.total_customers.value ?? metrics.total_customers) : metrics?.unique_customers?.value ?? 0],
          ["Revenue", metrics?.revenue && metrics.revenue.available ? `$${Number(metrics.revenue.value).toLocaleString()}` : "Unavailable"],
          ["Average LTV", metrics?.average_lifetime_value && metrics.average_lifetime_value.available ? `$${Number(metrics.average_lifetime_value.value).toLocaleString()}` : "Unavailable"],
        ].map(([label, value]) => (
          <Card key={String(label)} className="p-5">
            <div className="text-xs text-muted-foreground">{label}</div>
            <div className="mt-1 text-2xl font-bold">{value}</div>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {charts.length === 0 && (
          <Card className="p-6">
            <p className="text-sm text-muted-foreground">No suitable chart can be generated from this dataset.</p>
          </Card>
        )}

        {charts.map((c: any, idx: number) => (
          <Chart key={idx} title={c.title ?? c.type}>
            {c.type === "line" && (
              <LineChart data={c.data}>
                <Grid />
                <XAxis dataKey={c.x_key} />
                <YAxis />
                <Tooltip />
                <Line dataKey={c.y_key ?? "value"} stroke={colors[idx % colors.length]} strokeWidth={2.5} />
              </LineChart>
            )}

            {c.type === "area" && (
              <AreaChart data={c.data}>
                <Grid />
                <XAxis dataKey={c.x_key} />
                <YAxis />
                <Tooltip />
                <Area dataKey={c.y_key ?? "value"} stroke={colors[idx % colors.length]} fill={colors[idx % colors.length]} fillOpacity={0.25} />
              </AreaChart>
            )}

            {c.type === "bar" && (
              <BarChart data={c.data}>
                <Grid />
                <XAxis dataKey={c.x_key} />
                <YAxis />
                <Tooltip />
                <Bar dataKey={c.y_key ?? "value"} fill={colors[idx % colors.length]}>
                  {c.data.map((_: any, i: number) => (
                    <Cell key={i} fill={colors[i % colors.length]} />
                  ))}
                </Bar>
              </BarChart>
            )}

            {c.type === "pie" && (
              <PieChart>
                <Pie data={c.data} dataKey={c.y_key ?? "value"} nameKey={c.x_key} outerRadius={90}>
                  {c.data.map((_: any, i: number) => (
                    <Cell key={i} fill={colors[i % colors.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            )}

            {c.type === "scatter" && (
              <ScatterChart data={c.data}>
                <Grid />
                <XAxis dataKey={c.x_key} />
                <YAxis />
                <Tooltip />
                <Scatter data={c.data} fill={colors[idx % colors.length]} />
              </ScatterChart>
            )}
          </Chart>
        ))}
      </div>
    </div>
  );
}

function Grid() {
  return <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />;
}

function Chart({ title, children }: { title: string; children: React.ReactElement }) {
  return (
    <Card className="p-6">
      <h3 className="font-semibold">{title}</h3>
      <div className="mt-4 h-64">
        <ResponsiveContainer width="100%" height="100%">{children}</ResponsiveContainer>
      </div>
    </Card>
  );
}
