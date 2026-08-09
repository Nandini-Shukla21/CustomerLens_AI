import React, { useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { PageHeader } from "@/components/ui/PageHeader";
import { platformApi } from "@/api/platform";

export const Route = createFileRoute("/_app/copilot")({ component: CopilotPage });

type Message = { role: "user" | "assistant"; content: string; sources?: string[]; confidence?: number; filename?: string | null; retrievedChunks?: number; similarityScore?: number };

function CopilotPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [selectedDatasetId, setSelectedDatasetId] = useState("");
  const chat = useMutation({ mutationFn: (question: string) => platformApi.copilot(question, selectedDatasetId || undefined) });
  const datasets = useQuery({ queryKey: ["datasets"], queryFn: platformApi.datasets });
  const documents = useQuery({ queryKey: ["documents"], queryFn: platformApi.documents });

  React.useEffect(() => {
    if (datasets.data?.length && !selectedDatasetId) {
      setSelectedDatasetId(datasets.data[0].id);
    }
  }, [datasets.data, selectedDatasetId]);

  const send = async () => {
    const question = input.trim();
    if (!question) return;
    setMessages((m) => [...m, { role: "user", content: question }]);
    setInput("");
    try {
      const r = await chat.mutateAsync(question);
      setMessages((m) => [...m, { role: "assistant", content: r.answer, sources: r.sources, confidence: r.confidence, filename: r.filename, retrievedChunks: r.retrieved_chunks, similarityScore: r.similarity_score }]);
    } catch (e) {
      setMessages((m) => [...m, { role: "assistant", content: e instanceof Error ? e.message : "Unable to query uploaded documents." }]);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader eyebrow="AI Copilot" title="Ask your uploaded data" description="Copilot answers from datasets and knowledge documents with retrieved context and confidence scores." />
      <Card className="p-5">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 className="font-semibold">Available sources</h3>
            <p className="mt-2 text-sm text-muted-foreground">Datasets: {(datasets.data ?? []).map((d) => d.filename).join(", ") || "None"}</p>
            <p className="mt-1 text-sm text-muted-foreground">Documents: {(documents.data ?? []).map((d) => d.filename).join(", ") || "None"}</p>
          </div>
          <div className="max-w-xs">
            <label className="block text-xs font-semibold text-muted-foreground">Dataset</label>
            <select
              className="mt-2 w-full rounded border p-2"
              value={selectedDatasetId}
              onChange={(e) => setSelectedDatasetId(e.target.value)}
            >
              <option value="">Use most recent dataset</option>
              {(datasets.data ?? []).map((dataset) => (
                <option key={dataset.id} value={dataset.id}>
                  {dataset.filename}
                </option>
              ))}
            </select>
          </div>
        </div>
      </Card>
      <Card className="p-6">
        <div className="space-y-4">
          {messages.map((m, i) => (
            <div key={i} className={m.role === "user" ? "ml-auto max-w-3xl rounded bg-primary p-3 text-primary-foreground" : "max-w-3xl rounded bg-muted p-3"}>
              <div>{m.content}</div>
              {m.sources && (
                <div className="mt-2 text-xs opacity-75">
                  Sources: {m.sources.join(", ")} · Confidence {(m.confidence! * 100).toFixed(0)}% · {m.filename ? `File: ${m.filename}` : "File: n/a"} · Chunks: {m.retrievedChunks ?? 0} · Similarity: {(m.similarityScore ?? 0).toFixed(2)}
                </div>
              )}
            </div>
          ))}
        </div>
        <div className="mt-5 flex gap-2">
          <Textarea value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask about uploaded documents, datasets, or both…" />
          <Button disabled={!input.trim() || chat.isPending} onClick={send}>Ask</Button>
        </div>
      </Card>
    </div>
  );
}
