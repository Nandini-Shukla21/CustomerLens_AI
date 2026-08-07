import React from "react";
import { createFileRoute } from "@tanstack/react-router";
import {
  Database,
  FileSpreadsheet,
  BarChart3,
  Columns3,
  Rows3,
  Download,
  MessageSquare,
  RefreshCw,
} from "lucide-react";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { StatCard } from "@/components/ui/StatCard";
import { PageHeader } from "@/components/ui/PageHeader";

import { useQuery } from "@tanstack/react-query";
import { platformApi } from "@/api/platform";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export const Route = createFileRoute("/_app/dashboard")({
  head: () => ({
    meta: [
      {
        title: "Dataset Dashboard — CustomerLens AI",
      },
    ],
  }),
  component: DashboardPage,
});

type ColumnInfo = {
  name: string;
  type: string;
  missing: number;
  unique: number;
};

type DatasetRow = Record<string, unknown>;

const chartColors = [
  "#6366f1",
  "#8b5cf6",
  "#14b8a6",
  "#f59e0b",
  "#ef4444",
  "#06b6d4",
  "#ec4899",
  "#84cc16",
];

function DashboardPage() {
  const {
    data: datasets = [],
    isLoading: datasetsLoading,
  } = useQuery({
    queryKey: ["datasets"],
    queryFn: platformApi.datasets,
  });

  const [selectedDatasetId, setSelectedDatasetId] =
    React.useState<string>("");

  React.useEffect(() => {
    if (
      datasets.length > 0 &&
      !selectedDatasetId
    ) {
      setSelectedDatasetId(datasets[0].id);
    }
  }, [datasets, selectedDatasetId]);

  const selectedDataset = datasets.find(
    (dataset) => dataset.id === selectedDatasetId
  );

  const {
    data: columns = [],
    isLoading: columnsLoading,
  } = useQuery({
    queryKey: [
      "dataset-columns",
      selectedDatasetId,
    ],
    queryFn: () =>
      platformApi.datasetColumns(
        selectedDatasetId
      ),
    enabled: Boolean(selectedDatasetId),
  });

  const {
    data: preview,
    isLoading: previewLoading,
  } = useQuery({
    queryKey: [
      "dataset-preview",
      selectedDatasetId,
    ],
    queryFn: () =>
      platformApi.datasetPreview(
        selectedDatasetId,
        0,
        "",
        200
      ),
    enabled: Boolean(selectedDatasetId),
  });

  const rows: DatasetRow[] = preview?.rows || [];

  const numericColumns: ColumnInfo[] =
    columns.filter((column: ColumnInfo) =>
      isNumericType(column.type)
    );

  const categoricalColumns: ColumnInfo[] =
    columns.filter(
      (column: ColumnInfo) =>
        !isNumericType(column.type)
    );

  const numericChartData =
    numericColumns
      .slice(0, 2)
      .map((column) =>
        createNumericChartData(
          rows,
          column.name
        )
      );

  const categoricalChartData =
    categoricalColumns
      .slice(0, 2)
      .map((column) =>
        createCategoricalChartData(
          rows,
          column.name
        )
      );

  const isLoading =
    datasetsLoading ||
    columnsLoading ||
    previewLoading;

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Dataset Dashboard"
        title="Data Explorer"
        description={
          selectedDataset
            ? `Visual analysis of ${selectedDataset.filename}`
            : "Select an uploaded dataset to explore its data."
        }
        actions={
          <>
            <Button
              variant="outline"
              size="sm"
              onClick={() =>
                window.location.reload()
              }
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh
            </Button>

            <Button
              variant="outline"
              size="sm"
            >
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>

            <Button
              size="sm"
              className="bg-brand-gradient text-primary-foreground shadow-elegant hover:opacity-95"
            >
              <MessageSquare className="mr-2 h-4 w-4" />
              Ask Copilot
            </Button>
          </>
        }
      />

      {/* DATASET SELECTOR */}

      <Card className="border-border/60 bg-card/80 p-6 shadow-card">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Database className="h-5 w-5 text-brand" />

              <h3 className="text-base font-semibold">
                Select Dataset
              </h3>
            </div>

            <p className="mt-1 text-xs text-muted-foreground">
              Choose which uploaded dataset you
              want to analyze.
            </p>
          </div>

          <div className="w-full md:w-[350px]">
            <select
              value={selectedDatasetId}
              onChange={(event) =>
                setSelectedDatasetId(
                  event.target.value
                )
              }
              className="w-full rounded-lg border border-border bg-background px-4 py-3 text-sm outline-none focus:border-brand"
            >
              {datasets.length === 0 && (
                <option value="">
                  No datasets uploaded
                </option>
              )}

              {datasets.map((dataset) => (
                <option
                  key={dataset.id}
                  value={dataset.id}
                >
                  {dataset.filename}
                </option>
              ))}
            </select>
          </div>
        </div>
      </Card>

      {/* LOADING */}

      {isLoading && (
        <Card className="border-border/60 bg-card/80 p-8 text-center shadow-card">
          <RefreshCw className="mx-auto h-6 w-6 animate-spin text-brand" />

          <p className="mt-3 text-sm text-muted-foreground">
            Loading dataset...
          </p>
        </Card>
      )}

      {/* DATASET INFORMATION */}

      {!isLoading && selectedDataset && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              label="Total records"
              value={selectedDataset.rows.toLocaleString()}
              delta="Selected dataset"
              trend="up"
              icon={Rows3}
              data={[]}
            />

            <StatCard
              label="Total columns"
              value={selectedDataset.columns.toLocaleString()}
              delta="Dataset structure"
              trend="up"
              icon={Columns3}
              data={[]}
            />

            <StatCard
              label="Numeric columns"
              value={numericColumns.length.toLocaleString()}
              delta="Detected automatically"
              trend="up"
              icon={BarChart3}
              data={[]}
            />

            <StatCard
              label="Categorical columns"
              value={categoricalColumns.length.toLocaleString()}
              delta="Detected automatically"
              trend="up"
              icon={FileSpreadsheet}
              data={[]}
            />
          </div>

          {/* DATASET DETAILS */}

          <Card className="border-border/60 bg-card/80 p-6 shadow-card">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold">
                  Dataset information
                </h3>

                <p className="text-xs text-muted-foreground">
                  Columns detected in{" "}
                  {selectedDataset.filename}
                </p>
              </div>

              <Badge variant="outline">
                {rows.length} rows loaded
              </Badge>
            </div>

            <div className="mt-5 flex flex-wrap gap-2">
              {columns.map(
                (column: ColumnInfo) => (
                  <Badge
                    key={column.name}
                    variant="outline"
                    className="px-3 py-1"
                  >
                    {column.name}
                    <span className="ml-2 text-muted-foreground">
                      {column.type}
                    </span>
                  </Badge>
                )
              )}
            </div>
          </Card>

          {/* GRAPHS */}

          <div className="grid gap-4 lg:grid-cols-2">
            {numericChartData.map(
              (chart, index) => (
                <NumericChart
                  key={`numeric-${chart.column}`}
                  title={`${chart.column} distribution`}
                  column={chart.column}
                  data={chart.data}
                  color={
                    chartColors[index %
                      chartColors.length]
                  }
                />
              )
            )}

            {categoricalChartData.map(
              (chart, index) => (
                <CategoricalChart
                  key={`category-${chart.column}`}
                  title={`${chart.column} distribution`}
                  column={chart.column}
                  data={chart.data}
                />
              )
            )}
          </div>

          {/* NO GRAPH MESSAGE */}

          {numericChartData.length === 0 &&
            categoricalChartData.length ===
              0 && (
              <Card className="border-border/60 bg-card/80 p-10 text-center shadow-card">
                <BarChart3 className="mx-auto h-10 w-10 text-muted-foreground" />

                <h3 className="mt-4 text-base font-semibold">
                  No chartable columns found
                </h3>

                <p className="mt-2 text-sm text-muted-foreground">
                  This dataset does not contain
                  enough numeric or categorical
                  columns to generate charts.
                </p>
              </Card>
            )}

          {/* RAW DATA PREVIEW */}

          <Card className="border-border/60 bg-card/80 p-6 shadow-card">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold">
                  Data preview
                </h3>

                <p className="text-xs text-muted-foreground">
                  First {rows.length} records from{" "}
                  {selectedDataset.filename}
                </p>
              </div>

              <Badge variant="outline">
                {selectedDataset.rows.toLocaleString()} total
              </Badge>
            </div>

            <div className="mt-5 overflow-x-auto">
              {rows.length > 0 ? (
                <table className="w-full min-w-[700px] text-sm">
                  <thead>
                    <tr className="border-b border-border">
                      {columns.map(
                        (column: ColumnInfo) => (
                          <th
                            key={column.name}
                            className="px-4 py-3 text-left font-semibold"
                          >
                            {column.name}
                          </th>
                        )
                      )}
                    </tr>
                  </thead>

                  <tbody>
                    {rows
                      .slice(0, 10)
                      .map((row, rowIndex) => (
                        <tr
                          key={rowIndex}
                          className="border-b border-border/50"
                        >
                          {columns.map(
                            (
                              column: ColumnInfo
                            ) => (
                              <td
                                key={column.name}
                                className="px-4 py-3 text-muted-foreground"
                              >
                                {String(
                                  row[
                                    column.name
                                  ] ?? "-"
                                )}
                              </td>
                            )
                          )}
                        </tr>
                      ))}
                  </tbody>
                </table>
              ) : (
                <p className="py-8 text-center text-sm text-muted-foreground">
                  No records available.
                </p>
              )}
            </div>
          </Card>
        </>
      )}
    </div>
  );
}

/* ============================================================
   NUMERIC COLUMN HELPERS
   ============================================================ */

function isNumericType(type: string) {
  const normalized =
    type.toLowerCase();

  return (
    normalized.includes("int") ||
    normalized.includes("float") ||
    normalized.includes("double") ||
    normalized.includes("decimal") ||
    normalized.includes("number")
  );
}

function createNumericChartData(
  rows: DatasetRow[],
  column: string
) {
  const values = rows
    .map((row) =>
      Number(row[column])
    )
    .filter((value) =>
      Number.isFinite(value)
    );

  if (values.length === 0) {
    return {
      column,
      data: [],
    };
  }

  const min = Math.min(...values);
  const max = Math.max(...values);

  if (min === max) {
    return {
      column,
      data: [
        {
          range: String(min),
          count: values.length,
        },
      ],
    };
  }

  const bucketCount = 8;
  const bucketSize =
    (max - min) / bucketCount;

  const buckets = Array.from(
    { length: bucketCount },
    (_, index) => ({
      range: `${formatNumber(
        min + index * bucketSize
      )} - ${formatNumber(
        min +
          (index + 1) *
            bucketSize
      )}`,
      count: 0,
    })
  );

  values.forEach((value) => {
    let index = Math.floor(
      (value - min) /
        bucketSize
    );

    if (index >= bucketCount) {
      index = bucketCount - 1;
    }

    buckets[index].count += 1;
  });

  return {
    column,
    data: buckets,
  };
}

/* ============================================================
   CATEGORICAL COLUMN HELPERS
   ============================================================ */

function createCategoricalChartData(
  rows: DatasetRow[],
  column: string
) {
  const counts: Record<
    string,
    number
  > = {};

  rows.forEach((row) => {
    const value = String(
      row[column] ?? "Unknown"
    );

    counts[value] =
      (counts[value] || 0) + 1;
  });

  return {
    column,
    data: Object.entries(counts)
      .sort(
        (a, b) => b[1] - a[1]
      )
      .slice(0, 10)
      .map(
        ([name, value]) => ({
          name,
          value,
        })
      ),
  };
}

function formatNumber(
  value: number
) {
  if (
    Math.abs(value) >= 1000
  ) {
    return value.toLocaleString(
      undefined,
      {
        maximumFractionDigits: 0,
      }
    );
  }

  return value.toFixed(1);
}

/* ============================================================
   NUMERIC CHART
   ============================================================ */

function NumericChart({
  title,
  column,
  data,
  color,
}: {
  title: string;
  column: string;
  data: {
    range: string;
    count: number;
  }[];
  color: string;
}) {
  return (
    <Card className="border-border/60 bg-card/80 p-6 shadow-card">
      <div>
        <h3 className="text-base font-semibold">
          {title}
        </h3>

        <p className="text-xs text-muted-foreground">
          Automatically generated from{" "}
          {column}
        </p>
      </div>

      <div className="mt-6 h-72">
        <ResponsiveContainer
          width="100%"
          height="100%"
        >
          <BarChart
            data={data}
            margin={{
              top: 5,
              right: 10,
              bottom: 40,
              left: 0,
            }}
          >
            <CartesianGrid
              stroke="var(--border)"
              strokeDasharray="3 3"
              vertical={false}
            />

            <XAxis
              dataKey="range"
              angle={-25}
              textAnchor="end"
              height={65}
              stroke="var(--muted-foreground)"
              fontSize={10}
            />

            <YAxis
              stroke="var(--muted-foreground)"
              fontSize={11}
            />

            <Tooltip
              contentStyle={{
                background: "var(--popover)",
                border: "1px solid var(--border)",
                borderRadius: 10,
                fontSize: 12,
                color: "#facc15",
              }}
              itemStyle={{
                color: "#facc15",
                fontWeight: 600,
              }}
              labelStyle={{
                color: "#facc15",
                fontWeight: 600,
              }}
            />

            <Bar
              dataKey="count"
              name="Records"
              fill={color}
              radius={[
                6,
                6,
                0,
                0,
              ]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}

/* ============================================================
   CATEGORICAL CHART
   ============================================================ */

function CategoricalChart({
  title,
  column,
  data,
}: {
  title: string;
  column: string;
  data: {
    name: string;
    value: number;
  }[];
}) {
  return (
    <Card className="border-border/60 bg-card/80 p-6 shadow-card">
      <div>
        <h3 className="text-base font-semibold">
          {title}
        </h3>

        <p className="text-xs text-muted-foreground">
          Top categories from {column}
        </p>
      </div>

      <div className="mt-6 h-72">
        <ResponsiveContainer
          width="100%"
          height="100%"
        >
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              innerRadius={55}
              outerRadius={90}
              paddingAngle={3}
              stroke="none"
            >
              {data.map(
                (_, index) => (
                  <Cell
                    key={index}
                    fill={
                      chartColors[
                        index %
                          chartColors.length
                      ]
                    }
                  />
                )
              )}
            </Pie>

            <Tooltip
              contentStyle={{
                background: "var(--popover)",
                border: "1px solid var(--border)",
                borderRadius: 10,
                fontSize: 12,
                color: "#facc15",
              }}
              itemStyle={{
                color: "#facc15",
                fontWeight: 600,
              }}
              labelStyle={{
                color: "#facc15",
                fontWeight: 600,
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-2 space-y-2">
        {data
          .slice(0, 6)
          .map(
            (item, index) => (
              <div
                key={item.name}
                className="flex items-center justify-between text-sm"
              >
                <div className="flex items-center gap-2">
                  <span
                    className="h-2.5 w-2.5 rounded-full"
                    style={{
                      background:
                        chartColors[
                          index %
                            chartColors.length
                        ],
                    }}
                  />

                  <span className="max-w-[200px] truncate">
                    {item.name}
                  </span>
                </div>

                <span className="font-medium">
                  {item.value}
                </span>
              </div>
            )
          )}
      </div>
    </Card>
  );
}