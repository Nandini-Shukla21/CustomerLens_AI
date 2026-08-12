import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/PageHeader";
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
  Scatter,
  ScatterChart,
  ZAxis,
} from "recharts";

export const Route = createFileRoute("/_app/analytics")({
  component: AnalyticsPage,
});

// ============================================================
// COLORS
// ============================================================

const colors = [
  "#6366f1",
  "#8b5cf6",
  "#14b8a6",
  "#f59e0b",
  "#ef4444",
];

// Specific colors for scatter plots
const scatterColors = {
  experience: "#22c55e", // Green
  wlb: "#f97316", // Orange
};

// ============================================================
// ANALYTICS PAGE
// ============================================================

function AnalyticsPage() {
  const [selectedDatasetId, setSelectedDatasetId] = useState("");

  // ==========================================================
  // DATASETS
  // ==========================================================

  const { data: datasets = [] } = useQuery({
    queryKey: ["datasets"],
    queryFn: platformApi.datasets,
  });

  // Automatically select first dataset
  useEffect(() => {
    if (datasets.length > 0 && !selectedDatasetId) {
      setSelectedDatasetId(datasets[0].id);
    }
  }, [datasets, selectedDatasetId]);

  // ==========================================================
  // ANALYTICS
  // ==========================================================

  const {
    data,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["analytics", selectedDatasetId],
    queryFn: () =>
      platformApi.analytics(
        selectedDatasetId || undefined,
      ),
    enabled:
      datasets.length === 0 ||
      Boolean(selectedDatasetId),
  });

  // ==========================================================
  // METRICS
  // ==========================================================

  const metrics =
    data?.metrics ??
    data?.kpis ??
    {};

  const charts = data?.charts ?? [];

  // ==========================================================
  // RENDER
  // ==========================================================

  return (
    <div className="space-y-6">

      {/* ======================================================
          HEADER
      ====================================================== */}

      <PageHeader
        eyebrow="Analytics"
        title="Dataset analytics"
        description="Explore metrics and charts computed from the selected dataset."
      />

      {/* ======================================================
          DATASET SELECTOR
      ====================================================== */}

      <Card className="p-5">

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">

          <div>
            <h2 className="text-sm font-semibold">
              Dataset
            </h2>

            <p className="text-xs text-muted-foreground">
              Choose which dataset should power the analytics.
            </p>
          </div>

          <select
            value={selectedDatasetId}
            onChange={(event) =>
              setSelectedDatasetId(event.target.value)
            }
            className="
              max-w-xs
              rounded-md
              border
              border-blue-500/40
              bg-background
              px-3
              py-2
              text-sm
              font-medium
              text-blue-600
              outline-none
              transition
              focus:border-blue-500
              focus:ring-2
              focus:ring-blue-500/20
              dark:text-blue-400
            "
            style={{
              color: "#2563eb",
            }}
          >
            <option
              value=""
              style={{
                color: "#2563eb",
                backgroundColor: "#ffffff",
              }}
            >
              Use most recent dataset
            </option>

            {datasets.map((dataset) => (
              <option
                key={dataset.id}
                value={dataset.id}
                style={{
                  color: "#2563eb",
                  backgroundColor: "#ffffff",
                }}
              >
                {dataset.filename}
              </option>
            ))}
          </select>

        </div>
      </Card>

      {/* ======================================================
          LOADING / ERROR
      ====================================================== */}

      {isLoading && (
        <Card className="p-5">
          <p className="text-sm text-muted-foreground">
            Loading uploaded dataset analytics…
          </p>
        </Card>
      )}

      {error && (
        <Card className="p-5">
          <p className="text-sm text-destructive">
            {error instanceof Error
              ? error.message
              : "Unable to load analytics."}
          </p>
        </Card>
      )}

      {/* ======================================================
          KPI CARDS
      ====================================================== */}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

        {/* RECORDS */}

        <Card className="p-5">
          <div className="text-xs text-muted-foreground">
            Records
          </div>

          <div className="mt-1 text-2xl font-bold">
            {Number(
              data?.records ??
                metrics?.records?.value ??
                0,
            ).toLocaleString()}
          </div>
        </Card>

        {/* CUSTOMERS */}

        <Card className="p-5">
          <div className="text-xs text-muted-foreground">
            Customers
          </div>

          <div className="mt-1 text-2xl font-bold">
            {Number(
              metrics?.total_customers
                ? (
                    metrics.total_customers.value ??
                    metrics.total_customers
                  )
                : metrics?.unique_customers?.value ??
                  0,
            ).toLocaleString()}
          </div>
        </Card>

        {/* REVENUE */}

        <Card className="p-5">
          <div className="text-xs text-muted-foreground">
            Revenue
          </div>

          <div className="mt-1 text-2xl font-bold">
            {metrics?.revenue &&
            metrics.revenue.available
              ? `$${Number(
                  metrics.revenue.value,
                ).toLocaleString()}`
              : "Unavailable"}
          </div>
        </Card>

        {/* LTV */}

        <Card className="p-5">
          <div className="text-xs text-muted-foreground">
            Average LTV
          </div>

          <div className="mt-1 text-2xl font-bold">
            {metrics?.average_lifetime_value &&
            metrics.average_lifetime_value.available
              ? `$${Number(
                  metrics.average_lifetime_value.value,
                ).toLocaleString()}`
              : "Unavailable"}
          </div>
        </Card>

      </div>

      {/* ======================================================
          CHARTS
      ====================================================== */}

      <div className="grid gap-4 lg:grid-cols-2">

        {charts.length === 0 && (
          <Card className="p-6">
            <p className="text-sm text-muted-foreground">
              No suitable chart can be generated from this dataset.
            </p>
          </Card>
        )}

        {charts.map((c: any, idx: number) => {

          /*
           * Identify scatter chart type.
           *
           * This lets us give:
           * - Experience vs Age -> green
           * - WLB vs Age -> orange
           */

          const chartTitle =
            String(c.title ?? c.type);

          const isExperienceScatter =
            c.type === "scatter" &&
            chartTitle
              .toLowerCase()
              .includes("experience");

          const isWlbScatter =
            c.type === "scatter" &&
            chartTitle
              .toLowerCase()
              .includes("wlb");

          let scatterColor = colors[idx % colors.length];

          if (isExperienceScatter) {
  scatterColor = scatterColors.experience;
} else if (isWlbScatter) {
  scatterColor = scatterColors.wlb;
}
          return (
            <Chart
              key={idx}
              title={chartTitle}
            >

              {/* =================================================
                  LINE CHART
              ================================================= */}

              {c.type === "line" && (
                <LineChart
                  data={c.data ?? []}
                  margin={{
                    top: 10,
                    right: 20,
                    left: 0,
                    bottom: 10,
                  }}
                >
                  <Grid />

                  <XAxis
                    dataKey={c.x_key}
                    tick={{
                      fontSize: 11,
                    }}
                  />

                  <YAxis
                    tick={{
                      fontSize: 11,
                    }}
                  />

                  <Tooltip />

                  <Line
                    type="monotone"
                    dataKey={
                      c.y_key ?? "value"
                    }
                    stroke={
                      colors[
                        idx %
                          colors.length
                      ]
                    }
                    strokeWidth={2.5}
                    dot={false}
                  />
                </LineChart>
              )}

              {/* =================================================
                  AREA CHART
              ================================================= */}

              {c.type === "area" && (
                <AreaChart
                  data={c.data ?? []}
                  margin={{
                    top: 10,
                    right: 20,
                    left: 0,
                    bottom: 10,
                  }}
                >
                  <Grid />

                  <XAxis
                    dataKey={c.x_key}
                    tick={{
                      fontSize: 11,
                    }}
                  />

                  <YAxis
                    tick={{
                      fontSize: 11,
                    }}
                  />

                  <Tooltip />

                  <Area
                    type="monotone"
                    dataKey={
                      c.y_key ?? "value"
                    }
                    stroke={
                      colors[
                        idx %
                          colors.length
                      ]
                    }
                    fill={
                      colors[
                        idx %
                          colors.length
                      ]
                    }
                    fillOpacity={0.22}
                    strokeWidth={2}
                  />
                </AreaChart>
              )}

              {/* =================================================
                  BAR CHART
              ================================================= */}

              {c.type === "bar" && (
                <BarChart
                  data={c.data ?? []}
                  margin={{
                    top: 10,
                    right: 20,
                    left: 0,
                    bottom: 10,
                  }}
                >
                  <Grid />

                  <XAxis
                    dataKey={c.x_key}
                    tick={{
                      fontSize: 11,
                    }}
                  />

                  <YAxis
                    tick={{
                      fontSize: 11,
                    }}
                  />

                  <Tooltip />

                  <Bar
                    dataKey={
                      c.y_key ?? "value"
                    }
                    radius={[
                      4,
                      4,
                      0,
                      0,
                    ]}
                  >
                    {(c.data ?? []).map(
                      (
                        _: any,
                        i: number,
                      ) => (
                        <Cell
                          key={i}
                          fill={
                            colors[
                              i %
                                colors.length
                            ]
                          }
                        />
                      ),
                    )}
                  </Bar>
                </BarChart>
              )}

              {/* =================================================
                  PIE CHART
              ================================================= */}

              {c.type === "pie" && (
                <PieChart>

                  <Pie
                    data={c.data ?? []}
                    dataKey={
                      c.y_key ?? "value"
                    }
                    nameKey={c.x_key}
                    outerRadius={90}
                    innerRadius={35}
                    paddingAngle={2}
                  >
                    {(c.data ?? []).map(
                      (
                        _: any,
                        i: number,
                      ) => (
                        <Cell
                          key={i}
                          fill={
                            colors[
                              i %
                                colors.length
                            ]
                          }
                        />
                      ),
                    )}
                  </Pie>

                  <Tooltip />

                </PieChart>
              )}

              {/* =================================================
                  EXPERIENCE VS AGE
              ================================================= */}

              {c.type === "scatter" &&
                isExperienceScatter && (
                  <ScatterChart
                    margin={{
                      top: 15,
                      right: 25,
                      bottom: 15,
                      left: 5,
                    }}
                  >

                    <CartesianGrid
                      stroke="var(--border)"
                      strokeDasharray="3 3"
                    />

                    <XAxis
                      type="number"
                      dataKey={c.x_key}
                      name="Age"
                      tick={{
                        fontSize: 11,
                      }}
                      label={{
                        value: "Age",
                        position:
                          "insideBottom",
                        offset: -5,
                      }}
                    />

                    <YAxis
                      type="number"
                      dataKey={c.y_key}
                      name="Experience"
                      tick={{
                        fontSize: 11,
                      }}
                      label={{
                        value:
                          "Experience",
                        angle: -90,
                        position:
                          "insideLeft",
                      }}
                    />

                    <ZAxis
                      range={[35, 35]}
                    />

                    <Tooltip
                      cursor={{
                        strokeDasharray:
                          "3 3",
                      }}
                      contentStyle={{
                        borderRadius:
                          "8px",
                        border:
                          "1px solid var(--border)",
                      }}
                      formatter={(
                        value: any,
                        name: any,
                      ) => [
                        value,
                        name,
                      ]}
                    />

                    <Scatter
                      name="Experience vs Age"
                      data={
                        c.data ?? []
                      }
                      fill={
                        scatterColor
                      }
                      fillOpacity={0.65}
                      line={false}
                    />

                  </ScatterChart>
                )}

              {/* =================================================
                  WLB VS AGE
              ================================================= */}

              {c.type === "scatter" &&
                isWlbScatter && (
                  <ScatterChart
                    margin={{
                      top: 15,
                      right: 25,
                      bottom: 15,
                      left: 5,
                    }}
                  >

                    <CartesianGrid
                      stroke="var(--border)"
                      strokeDasharray="3 3"
                    />

                    <XAxis
                      type="number"
                      dataKey={c.x_key}
                      name="Age"
                      tick={{
                        fontSize: 11,
                      }}
                      label={{
                        value: "Age",
                        position:
                          "insideBottom",
                        offset: -5,
                      }}
                    />

                    <YAxis
                      type="number"
                      dataKey={c.y_key}
                      name="WLB"
                      domain={[
                        "auto",
                        "auto",
                      ]}
                      tick={{
                        fontSize: 11,
                      }}
                      label={{
                        value:
                          "Work-Life Balance",
                        angle: -90,
                        position:
                          "insideLeft",
                      }}
                    />

                    <ZAxis
                      range={[45, 45]}
                    />

                    <Tooltip
                      cursor={{
                        strokeDasharray:
                          "3 3",
                      }}
                      contentStyle={{
                        borderRadius:
                          "8px",
                        border:
                          "1px solid var(--border)",
                      }}
                    />

                    <Scatter
                      name="Work-Life Balance vs Age"
                      data={
                        c.data ?? []
                      }
                      fill={
                        scatterColor
                      }
                      fillOpacity={0.7}
                      line={false}
                    />

                  </ScatterChart>
                )}

              {/* =================================================
                  FALLBACK SCATTER
              ================================================= */}

              {c.type === "scatter" &&
                !isExperienceScatter &&
                !isWlbScatter && (
                  <ScatterChart
                    margin={{
                      top: 15,
                      right: 25,
                      bottom: 15,
                      left: 5,
                    }}
                  >

                    <CartesianGrid
                      stroke="var(--border)"
                      strokeDasharray="3 3"
                    />

                    <XAxis
                      type="number"
                      dataKey={c.x_key}
                      name={c.x_key}
                    />

                    <YAxis
                      type="number"
                      dataKey={c.y_key}
                      name={c.y_key}
                    />

                    <ZAxis
                      range={[40, 40]}
                    />

                    <Tooltip />

                    <Scatter
                      data={
                        c.data ?? []
                      }
                      fill={
                        scatterColor
                      }
                      fillOpacity={0.65}
                    />

                  </ScatterChart>
                )}

            </Chart>
          );
        })}

      </div>

    </div>
  );
}

// ============================================================
// GRID
// ============================================================

function Grid() {
  return (
    <CartesianGrid
      stroke="var(--border)"
      strokeDasharray="3 3"
      vertical={false}
    />
  );
}

// ============================================================
// CHART WRAPPER
// ============================================================

function Chart({
  title,
  children,
}: {
  title: string;
  children: React.ReactElement;
}) {
  return (
    <Card className="p-6">

      <h3 className="font-semibold">
        {title}
      </h3>

      <div className="mt-4 h-64">
        <ResponsiveContainer
          width="100%"
          height="100%"
        >
          {children}
        </ResponsiveContainer>
      </div>

    </Card>
  );
}