import React, { useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useMutation, useQuery } from "@tanstack/react-query";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { PageHeader } from "@/components/ui/PageHeader";
import { platformApi } from "@/api/platform";

export const Route = createFileRoute("/_app/copilot")({
  component: CopilotPage,
});

type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
  confidence?: number;
  filename?: string | null;
  retrievedChunks?: number;
  similarityScore?: number;
};

function CopilotPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [selectedDatasetId, setSelectedDatasetId] = useState("");

  const chat = useMutation({
    mutationFn: (question: string) =>
      platformApi.copilot(
        question,
        selectedDatasetId || undefined,
      ),
  });

  const datasets = useQuery({
    queryKey: ["datasets"],
    queryFn: platformApi.datasets,
  });

  const documents = useQuery({
    queryKey: ["documents"],
    queryFn: platformApi.documents,
  });

  React.useEffect(() => {
    if (
      datasets.data?.length &&
      !selectedDatasetId
    ) {
      setSelectedDatasetId(datasets.data[0].id);
    }
  }, [datasets.data, selectedDatasetId]);

  const send = async () => {
    const question = input.trim();

    if (!question) return;

    setMessages((m) => [
      ...m,
      {
        role: "user",
        content: question,
      },
    ]);

    setInput("");

    try {
      const r = await chat.mutateAsync(question);

      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: r.answer,
          sources: r.sources,
          confidence: r.confidence,
          filename: r.filename,
          retrievedChunks: r.retrieved_chunks,
          similarityScore: r.similarity_score,
        },
      ]);
    } catch (e) {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content:
            e instanceof Error
              ? e.message
              : "Unable to query uploaded documents.",
        },
      ]);
    }
  };

  return (
    <div className="space-y-6">

      {/* ======================================================
          HEADER
      ====================================================== */}

      <PageHeader
        eyebrow="AI Copilot"
        title="Ask your uploaded data"
        description="Copilot answers from datasets and knowledge documents with retrieved context and confidence scores."
      />

      {/* ======================================================
          AVAILABLE SOURCES
      ====================================================== */}

      <Card className="p-5">

        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">

          <div>
            <h3 className="font-semibold">
              Available sources
            </h3>

            <p className="mt-2 text-sm text-muted-foreground">
              Datasets:{" "}
              {(datasets.data ?? [])
                .map((d) => d.filename)
                .join(", ") ||
                "None"}
            </p>

            <p className="mt-1 text-sm text-muted-foreground">
              Documents:{" "}
              {(documents.data ?? [])
                .map((d) => d.filename)
                .join(", ") ||
                "None"}
            </p>
          </div>

          {/* ==================================================
              DATASET SELECTOR
          ================================================== */}

          <div className="max-w-xs">
            <label className="block text-xs font-semibold text-muted-foreground">
              Dataset
            </label>

            <select
              className="
                mt-2
                w-full
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
              value={selectedDatasetId}
              onChange={(e) =>
                setSelectedDatasetId(
                  e.target.value,
                )
              }
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

              {(datasets.data ?? []).map(
                (dataset) => (
                  <option
                    key={dataset.id}
                    value={dataset.id}
                    style={{
                      color: "#2563eb",
                      backgroundColor:
                        "#ffffff",
                    }}
                  >
                    {dataset.filename}
                  </option>
                ),
              )}
            </select>
          </div>

        </div>
      </Card>

      {/* ======================================================
          CHAT
      ====================================================== */}

      <Card className="p-6">

        <div className="space-y-4">

          {messages.length === 0 && (
            <div className="rounded-lg border border-dashed p-6 text-center">
              <p className="font-medium">
                Ask Copilot anything about your data
              </p>

              <p className="mt-1 text-sm text-muted-foreground">
                Try asking about customers, trends,
                uploaded documents, or insights.
              </p>
            </div>
          )}

          {messages.map((m, i) => (
            <div
              key={i}
              className={
                m.role === "user"
                  ? "ml-auto max-w-3xl rounded bg-primary p-3 text-primary-foreground"
                  : "max-w-3xl rounded bg-muted p-3"
              }
            >
              <div>
                {m.content}
              </div>

              {m.sources && (
                <div className="mt-2 text-xs opacity-75">
                  Sources:{" "}
                  {m.sources.join(", ")}
                  {" · "}
                  Confidence{" "}
                  {(
                    (m.confidence ?? 0) *
                    100
                  ).toFixed(0)}
                  %
                  {" · "}
                  {m.filename
                    ? `File: ${m.filename}`
                    : "File: n/a"}
                  {" · "}
                  Chunks:{" "}
                  {m.retrievedChunks ?? 0}
                  {" · "}
                  Similarity:{" "}
                  {(
                    m.similarityScore ?? 0
                  ).toFixed(2)}
                </div>
              )}
            </div>
          ))}

        </div>

        {/* ==================================================
            INPUT
        ================================================== */}

        <div className="mt-5 flex gap-2">

          <Textarea
            value={input}
            onChange={(e) =>
              setInput(e.target.value)
            }
            placeholder="Ask about uploaded documents, datasets, or both…"
          />

          <Button
            disabled={
              !input.trim() ||
              chat.isPending
            }
            onClick={send}
          >
            {chat.isPending
              ? "Asking..."
              : "Ask"}
          </Button>

        </div>

      </Card>

    </div>
  );
}