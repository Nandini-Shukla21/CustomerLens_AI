import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";

import {
  Activity,
  Database,
  DollarSign,
  FileText,
  Upload,
  Users,
  TrendingUp,
} from "lucide-react";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatCard } from "@/components/ui/StatCard";

import { platformApi } from "@/api/platform";

export const Route = createFileRoute("/_app/home")({
  component: HomePage,
});

function HomePage() {
  const homeQuery = useQuery({
    queryKey: ["home-overview"],
    queryFn: platformApi.homeSummary,
    refetchInterval: 10000,
  });

  const meQuery = useQuery({
    queryKey: ["current-user"],
    queryFn: platformApi.me,
  });

  const data = homeQuery.data;

  if (homeQuery.isLoading) {
    return (
      <div className="p-6">
        <Card className="p-8">
          <p className="text-muted-foreground">
            Loading your workspace...
          </p>
        </Card>
      </div>
    );
  }

  if (homeQuery.isError) {
    return (
      <div className="p-6">
        <Card className="p-8">
          <h2 className="text-xl font-semibold">
            Unable to load workspace
          </h2>

          <p className="mt-2 text-muted-foreground">
            The Home API could not be loaded.
          </p>

          <p className="mt-2 text-sm text-red-500">
            {homeQuery.error instanceof Error
              ? homeQuery.error.message
              : "Unknown error"}
          </p>

          <Button
            className="mt-4"
            onClick={() => homeQuery.refetch()}
          >
            Try again
          </Button>
        </Card>
      </div>
    );
  }

  const stats = data?.stats;

  return (
    <div className="space-y-6 p-6">

      {/* ======================================================
          HEADER
      ====================================================== */}

      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm text-muted-foreground">
            Customer Intelligence Platform
          </p>

          <h1 className="text-3xl font-bold tracking-tight">
            Welcome back,{" "}
            {meQuery.data?.name ??
              meQuery.data?.email ??
              "User"}
          </h1>

          <p className="mt-1 text-muted-foreground">
            Your uploaded data is powering this live workspace.
          </p>
        </div>

        <Link to ="/upload">
          <Button>
            <Upload className="mr-2 h-4 w-4" />
            Upload data
          </Button>
        </Link>
      </div>

      {/* ======================================================
          STAT CARDS
      ====================================================== */}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">

        <StatCard
          label="Customers"
          value={Number(
            stats?.customers ?? 0
          ).toLocaleString()}
          delta="Live"
          trend="up"
          icon={Users}
          data={[]}
        />

        <StatCard
          label="Revenue"
          value={`$${Number(
            stats?.revenue ?? 0
          ).toLocaleString()}`}
          delta="Live"
          trend="up"
          icon={DollarSign}
          data={[]}
        />

        <StatCard
          label="Transactions"
          value={Number(
            stats?.transactions ?? 0
          ).toLocaleString()}
          delta="Live"
          trend="up"
          icon={Activity}
          data={[]}
        />

        <StatCard
          label="Datasets"
          value={Number(
            stats?.datasets ?? 0
          ).toLocaleString()}
          delta={`${stats?.documents ?? 0} documents`}
          trend="up"
          icon={Database}
          data={[]}
        />

      </div>

      {/* ======================================================
          DATA OVERVIEW
      ====================================================== */}

      <div className="grid gap-6 lg:grid-cols-2">

        {/* DATASETS */}

        <Card className="p-6">

          <div className="mb-5 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold">
                Your datasets
              </h2>

              <p className="text-sm text-muted-foreground">
                Recently uploaded datasets
              </p>
            </div>

            <Database className="h-5 w-5 text-muted-foreground" />
          </div>

          <div className="space-y-3">

            {(data?.datasets ?? [])
              .slice(0, 5)
              .map((dataset) => (
                <div
                  key={dataset.id}
                  className="flex items-center justify-between rounded-lg border p-3"
                >
                  <div className="flex items-center gap-3">

                    <Database className="h-4 w-4" />

                    <div>
                      <p className="font-medium">
                        {dataset.filename}
                      </p>

                      <p className="text-xs text-muted-foreground">
                        {dataset.rows.toLocaleString()} rows ·{" "}
                        {dataset.columns} columns
                      </p>
                    </div>

                  </div>
                </div>
              ))}

            {(data?.datasets ?? []).length === 0 && (
              <p className="text-sm text-muted-foreground">
                No datasets uploaded yet.
              </p>
            )}

          </div>
        </Card>

        {/* DOCUMENTS */}

        <Card className="p-6">

          <div className="mb-5 flex items-center justify-between">

            <div>
              <h2 className="text-lg font-semibold">
                Your documents
              </h2>

              <p className="text-sm text-muted-foreground">
                Documents available to Copilot
              </p>
            </div>

            <FileText className="h-5 w-5 text-muted-foreground" />

          </div>

          <div className="space-y-3">

            {(data?.documents ?? [])
              .slice(0, 5)
              .map((document) => (
                <div
                  key={document.id}
                  className="flex items-center justify-between rounded-lg border p-3"
                >

                  <div className="flex items-center gap-3">

                    <FileText className="h-4 w-4" />

                    <div>
                      <p className="font-medium">
                        {document.filename}
                      </p>

                      <p className="text-xs text-muted-foreground">
                        {document.status || "Document"}
                      </p>
                    </div>

                  </div>

                  <span className="rounded-full bg-green-500/10 px-2 py-1 text-xs text-green-500">
                    {document.status === "indexed"
                      ? "Ready"
                      : "Uploaded"}
                  </span>

                </div>
              ))}

            {(data?.documents ?? []).length === 0 && (
              <p className="text-sm text-muted-foreground">
                No documents uploaded yet.
              </p>
            )}

          </div>
        </Card>

      </div>

      {/* ======================================================
          ACTIVITY
      ====================================================== */}

      <Card className="p-6">

        <div className="mb-5 flex items-center justify-between">

          <div>
            <h2 className="text-lg font-semibold">
              Recent activity
            </h2>

            <p className="text-sm text-muted-foreground">
              What's happening in your workspace
            </p>
          </div>

          <TrendingUp className="h-5 w-5 text-muted-foreground" />

        </div>

        <div className="space-y-4">

          {(data?.recent_activity ?? [])
            .slice(0, 10)
            .map((item) => (

              <div
                key={item.id}
                className="flex items-start gap-3"
              >

                <div className="mt-1 flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
                  <Activity className="h-4 w-4" />
                </div>

                <div className="flex-1">

                  <p className="text-sm font-medium">
                    {item.action}
                    {item.entity_name
                      ? ` — ${item.entity_name}`
                      : ""}
                  </p>

                  <p className="text-xs text-muted-foreground">
                    {item.created_at}
                  </p>

                </div>

                <span className="text-xs capitalize text-muted-foreground">
                  {item.entity_type}
                </span>

              </div>

            ))}

          {(data?.recent_activity ?? []).length === 0 && (
            <p className="text-sm text-muted-foreground">
              No recent activity.
            </p>
          )}

        </div>

      </Card>

    </div>
  );
}