import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/PageHeader";
import { platformApi } from "@/api/platform";

export const Route = createFileRoute("/_app/reports")({ component: ReportsPage });

function ReportsPage() {
  const [selectedDatasetId, setSelectedDatasetId] = useState("");
  const { data: datasets = [] } = useQuery({ queryKey: ["datasets"], queryFn: platformApi.datasets });

  useEffect(() => {
    if (datasets.length > 0 && !selectedDatasetId) {
      setSelectedDatasetId(datasets[0].id);
    }
  }, [datasets, selectedDatasetId]);

  const q = useQuery({
    queryKey: ["report-dashboard", selectedDatasetId],
    queryFn: () => platformApi.reportsDashboard(selectedDatasetId || undefined),
    enabled: datasets.length === 0 || Boolean(selectedDatasetId),
  });

  const d = q.data;

  function renderMetric(v: any) {
    if (!v) return "Unavailable";
    if (typeof v === "number") return v.toLocaleString();
    if (v && typeof v === "object") return v.available ? (typeof v.value === "number" ? v.value.toLocaleString() : String(v.value)) : "Unavailable";
    return String(v);
  }

  return (
    <div className="space-y-6">
      <PageHeader eyebrow="Reports" title="Live portfolio report" description="Current summary generated from uploaded datasets." />

      <Card className="p-5">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-sm font-semibold">Dataset</h2>
            <p className="text-xs text-muted-foreground">Choose a dataset that backs the live report.</p>
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

      <div className="grid gap-4 md:grid-cols-3">
        {[
          ["Customers", d?.total_customers],
          ["Revenue", d?.revenue],
          ["Transactions", d?.transactions],
          ["High risk", d?.high_risk_customers],
          ["Churn signals", d?.predicted_churn],
          ["Datasets", d?.datasets],
        ].map(([k, v]) => (
          <Card className="p-5" key={String(k)}>
            <div className="text-sm text-muted-foreground">{k}</div>
            <div className="mt-1 text-2xl font-bold">{renderMetric(v)}</div>
          </Card>
        ))}
      </div>

      <Card className="p-6">
        <h3 className="font-semibold">Generated insights</h3>
        <ul className="mt-3 space-y-3">
          {(d?.ai_insights ?? []).map((i: { title: string; description: string }) => (
            <li key={i.title}>
              <b>{i.title}</b>
              <p className="text-sm text-muted-foreground">{i.description}</p>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}
