import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageHeader } from "@/components/ui/PageHeader";
import { platformApi } from "@/api/platform";

export const Route = createFileRoute("/_app/insights")({
  component: InsightsPage,
});

type Insight = {
  title: string;
  description: string;
  action?: string;
  priority?: string;
  confidence?: number;
  metric?: string;
  value?: number | string;
  source?: string | null;
};

function InsightsPage() {
  const [selectedDatasetId, setSelectedDatasetId] = useState("");

  const {
    data: datasets = [],
    isLoading: datasetsLoading,
    error: datasetsError,
  } = useQuery({
    queryKey: ["datasets"],
    queryFn: platformApi.datasets,
  });

  useEffect(() => {
    if (datasets.length > 0 && !selectedDatasetId) {
      setSelectedDatasetId(datasets[0].id);
    }
  }, [datasets, selectedDatasetId]);

  const {
    data: insightsData,
    isLoading: insightsLoading,
    error: insightsError,
  } = useQuery({
    queryKey: ["insights", selectedDatasetId],
    queryFn: () =>
      platformApi.insights(selectedDatasetId || undefined),
    enabled: datasets.length === 0 || Boolean(selectedDatasetId),
  });

  /*
   * The backend normally returns an array.
   * This also safely handles an object containing { insights: [...] }.
   */
  const insights: Insight[] = Array.isArray(insightsData)
    ? insightsData
    : Array.isArray((insightsData as any)?.insights)
      ? (insightsData as any).insights
      : [];

  const selectedDataset = datasets.find(
    (dataset) => dataset.id === selectedDatasetId
  );

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="AI Insights"
        title="Signals from uploaded data"
        description="Discover important patterns, trends, and anomalies automatically detected from your uploaded dataset."
      />

      {/* Dataset selector */}
      <Card className="p-5">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-sm font-semibold">Dataset</h2>

            <p className="mt-1 text-xs text-muted-foreground">
              Choose a dataset for insight generation.
            </p>

            {selectedDataset && (
              <p className="mt-2 text-xs text-blue-600 dark:text-blue-400">
                Analyzing: {selectedDataset.filename}
              </p>
            )}
          </div>

          <div className="w-full max-w-xs">
            <select
              value={selectedDatasetId}
              onChange={(event) =>
                setSelectedDatasetId(event.target.value)
              }
              className="
                w-full
                rounded-md
                border
                border-blue-300
                bg-white
                px-3
                py-2
                text-sm
                font-medium
                text-blue-700
                shadow-sm
                outline-none
                transition
                focus:border-blue-500
                focus:ring-2
                focus:ring-blue-500/20
                dark:border-blue-700
                dark:bg-slate-950
                dark:text-blue-300
              "
            >
              <option
                value=""
                className="bg-white text-blue-700 dark:bg-slate-950 dark:text-blue-300"
              >
                Use most recent dataset
              </option>

              {datasets.map((dataset) => (
                <option
                  key={dataset.id}
                  value={dataset.id}
                  className="bg-white text-blue-700 dark:bg-slate-950 dark:text-blue-300"
                >
                  {dataset.filename}
                </option>
              ))}
            </select>
          </div>
        </div>
      </Card>

      {/* Loading */}
      {(datasetsLoading || insightsLoading) && (
        <Card className="p-8">
          <div className="flex items-center gap-3">
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />

            <div>
              <p className="text-sm font-medium">
                Generating AI insights...
              </p>

              <p className="mt-1 text-xs text-muted-foreground">
                Analyzing patterns and statistics in your dataset.
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Errors */}
      {(datasetsError || insightsError) && (
        <Card className="border-red-300 p-6 dark:border-red-900">
          <h3 className="font-semibold text-red-600 dark:text-red-400">
            Unable to generate insights
          </h3>

          <p className="mt-2 text-sm text-muted-foreground">
            {datasetsError instanceof Error
              ? datasetsError.message
              : insightsError instanceof Error
                ? insightsError.message
                : "Something went wrong while analyzing the dataset."}
          </p>
        </Card>
      )}

      {/* Insight cards */}
      {!insightsLoading &&
        !insightsError &&
        insights.length > 0 && (
          <>
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold">
                  Key insights
                </h2>

                <p className="text-sm text-muted-foreground">
                  {insights.length} insights detected from your dataset.
                </p>
              </div>

              <Badge>
                AI Analysis
              </Badge>
            </div>

            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {insights.map((insight, index) => (
                <Card
                  key={`${insight.title}-${index}`}
                  className="
                    group
                    relative
                    overflow-hidden
                    p-6
                    transition-all
                    duration-200
                    hover:-translate-y-1
                    hover:shadow-lg
                  "
                >
                  {/* Accent line */}
                  <div className="absolute left-0 top-0 h-full w-1 bg-gradient-to-b from-blue-500 via-indigo-500 to-purple-500" />

                  <div className="flex items-start justify-between gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-500/10 text-lg">
                      ✦
                    </div>

                    {insight.priority && (
                      <Badge>
                        {insight.priority}
                      </Badge>
                    )}
                  </div>

                  <h3 className="mt-4 text-base font-semibold">
                    {insight.title}
                  </h3>

                  <p className="mt-2 text-sm leading-6 text-muted-foreground">
                    {insight.description}
                  </p>

                  {insight.action && (
                    <div className="mt-5 rounded-lg border border-blue-200 bg-blue-50 p-3 dark:border-blue-900/50 dark:bg-blue-950/30">
                      <p className="text-xs font-semibold text-blue-700 dark:text-blue-300">
                        Recommended action
                      </p>

                      <p className="mt-1 text-sm text-blue-900 dark:text-blue-100">
                        {insight.action}
                      </p>
                    </div>
                  )}

                  {typeof insight.confidence === "number" && (
                    <div className="mt-5">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-muted-foreground">
                          Confidence
                        </span>

                        <span className="font-semibold">
                          {(insight.confidence * 100).toFixed(0)}%
                        </span>
                      </div>

                      <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-muted">
                        <div
                          className="h-full rounded-full bg-blue-500 transition-all"
                          style={{
                            width: `${Math.min(
                              100,
                              Math.max(
                                0,
                                insight.confidence * 100
                              )
                            )}%`,
                          }}
                        />
                      </div>
                    </div>
                  )}

                  {insight.source && (
                    <p className="mt-4 truncate text-xs text-muted-foreground">
                      Source: {insight.source}
                    </p>
                  )}
                </Card>
              ))}
            </div>
          </>
        )}

      {/* Empty state */}
      {!insightsLoading &&
        !insightsError &&
        insights.length === 0 && (
          <Card className="p-10 text-center">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-blue-500/10 text-xl">
              ✦
            </div>

            <h3 className="mt-4 font-semibold">
              No insights available
            </h3>

            <p className="mx-auto mt-2 max-w-md text-sm text-muted-foreground">
              Upload a dataset containing numeric or categorical
              information and the AI Insights engine will automatically
              identify useful patterns.
            </p>
          </Card>
        )}
    </div>
  );
}