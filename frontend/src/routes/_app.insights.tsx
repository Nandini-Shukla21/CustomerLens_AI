import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageHeader } from "@/components/ui/PageHeader";
import { platformApi } from "@/api/platform";

export const Route = createFileRoute("/_app/insights")({ component: InsightsPage });

function InsightsPage() {
  const [selectedDatasetId, setSelectedDatasetId] = useState("");
  const { data: datasets = [] } = useQuery({ queryKey: ["datasets"], queryFn: platformApi.datasets });

  useEffect(() => {
    if (datasets.length > 0 && !selectedDatasetId) {
      setSelectedDatasetId(datasets[0].id);
    }
  }, [datasets, selectedDatasetId]);

  const q = useQuery({
    queryKey: ["insights", selectedDatasetId],
    queryFn: () => platformApi.insights(selectedDatasetId || undefined),
    enabled: datasets.length === 0 || Boolean(selectedDatasetId),
  });

  return (
    <div className="space-y-6">
      <PageHeader eyebrow="AI Insights" title="Signals from uploaded data" description="Insights are generated from your uploaded datasets." />

      <Card className="p-5">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-sm font-semibold">Dataset</h2>
            <p className="text-xs text-muted-foreground">Choose a dataset for insight generation.</p>
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

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {(q.data ?? []).map((i: any) => (
          <Card key={i.title} className="p-6">
            {i.priority && <Badge>{i.priority}</Badge>}
            <h3 className="mt-3 font-semibold">{i.title}</h3>
            <p className="mt-2 text-sm text-muted-foreground">{i.description}</p>
            {i.action && <p className="mt-4 text-sm"><b>Recommended action:</b> {i.action}</p>}
            {typeof i.confidence === "number" && (
              <p className="mt-3 text-xs text-muted-foreground">Confidence {(i.confidence * 100).toFixed(0)}%</p>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
