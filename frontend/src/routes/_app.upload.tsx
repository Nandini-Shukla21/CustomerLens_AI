import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  BrainCircuit,
  CheckCircle2,
  CloudUpload,
  Database,
  Download,
  File,
  FileSpreadsheet,
  FileText,
  Loader2,
  MoreHorizontal,
  Sparkles,
  Trash2,
  Wand2,
  Zap,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { PageHeader } from "@/components/ui/PageHeader";
import { platformApi } from "@/api/platform";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";

export const Route = createFileRoute("/_app/upload")({
  head: () => ({ meta: [{ title: "Upload Center — CustomerLens AI" }] }),
  component: UploadPage,
});

const STAGES = [
  { key: "upload", label: "Uploading", icon: CloudUpload, detail: "Streaming to secure storage" },
  { key: "parse", label: "Parsing", icon: FileText, detail: "Detecting delimiters + encoding" },
  { key: "clean", label: "Cleaning", icon: Wand2, detail: "Missing values + type coercion" },
  { key: "schema", label: "Detecting schema", icon: Database, detail: "Inferring 42 columns" },
  { key: "embed", label: "Generating embeddings", icon: BrainCircuit, detail: "text-embedding-3-large" },
  { key: "vector", label: "Vector database", icon: Database, detail: "Writing to pgvector" },
  { key: "rag", label: "Building RAG index", icon: Sparkles, detail: "Hybrid + reranker" },
  { key: "ready", label: "Ready", icon: CheckCircle2, detail: "Available to Copilot" },
] as const;

type Pipeline = { name: string; stage: number; startedAt: number };

function UploadPage() {
  const [drag, setDrag] = useState(false);
  const [uploading, setUploading] = useState<{ name: string; pct: number }[]>([]);
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const fileInput = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();
  const { data: datasets = [] } = useQuery({ queryKey: ["datasets"], queryFn: platformApi.datasets });
  const { data: documents = [] } = useQuery({ queryKey: ["documents"], queryFn: platformApi.documents });
  const upload = useMutation({
    mutationFn: (file: File) => platformApi.upload(file, (pct) => setUploading((items) => items.map((x) => x.name === file.name ? { ...x, pct } : x))),
    onSuccess: (result) => { setPipelines((p) => [...p, { name: result.filename, stage: 1, startedAt: Date.now() }]); queryClient.invalidateQueries({ queryKey: ["datasets"] }); queryClient.invalidateQueries({ queryKey: ["documents"] }); queryClient.invalidateQueries({ queryKey: ["dashboard"] }); toast.success(`${result.filename} uploaded successfully`); },
    onError: (error) => toast.error(error.message),
  });

  useEffect(() => {
    if (!pipelines.length) return;
    const id = setInterval(() => {
      setPipelines((ps) =>
        ps.map((p) => (p.stage < STAGES.length - 1 ? { ...p, stage: p.stage + 1 } : p)),
      );
    }, 900);
    return () => clearInterval(id);
  }, [pipelines.length]);

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDrag(false);
    const files = Array.from(e.dataTransfer.files);
    if (!files.length) return;
    files.forEach(uploadFile);
  };
  const uploadFile = (file: File) => { if (!/\.(csv|xlsx|xls|json|pdf|docx|txt|md|markdown)$/i.test(file.name)) { toast.error("Supported types: CSV, Excel, JSON, PDF, DOCX, TXT, and Markdown."); return; } setUploading((u) => [...u, { name: file.name, pct: 0 }]); upload.mutate(file); };

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Upload Center"
        title="Bring your data into CustomerLens"
        description="Drop datasets or documents to power dashboards, RAG, and predictive models. Supports CSV, Excel, JSON, PDF, DOCX, TXT."
      />

      <Card
        onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onDrop={onDrop}
        className={`relative overflow-hidden border-2 border-dashed p-12 text-center transition-colors ${drag ? "border-primary bg-primary/5" : "border-border/70 bg-card/70"}`}
      >
        <div className="pointer-events-none absolute inset-0 bg-brand-gradient opacity-[0.04]" />
        <div className="relative">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-gradient text-primary-foreground shadow-elegant">
            <CloudUpload className="h-8 w-8" />
          </div>
          <h3 className="mt-4 text-lg font-semibold">Drag & drop files here</h3>
          <p className="mt-1 text-sm text-muted-foreground">or click to browse · max 5GB per file · encrypted in transit and at rest</p>
          <div className="mt-5 flex flex-wrap items-center justify-center gap-2">
            <input ref={fileInput} type="file" multiple accept=".csv,.xlsx,.xls,.json,.pdf,.docx,.txt,.md,.markdown" className="hidden" onChange={(e) => { Array.from(e.target.files ?? []).forEach(uploadFile); e.currentTarget.value = ""; }} />
            <Button
              onClick={() => fileInput.current?.click()}
              className="bg-brand-gradient text-primary-foreground shadow-elegant hover:opacity-95"
            >
              Browse files
            </Button>
            <Button variant="outline">Connect Snowflake</Button>
            <Button variant="outline">Connect S3</Button>
          </div>
          <div className="mt-5 flex flex-wrap justify-center gap-2 text-[11px] text-muted-foreground">
            {["CSV","Excel","JSON","PDF","DOCX","TXT","Markdown"].map((t) => (
              <span key={t} className="rounded-full border border-border/60 bg-background/60 px-2.5 py-0.5">{t}</span>
            ))}
          </div>
        </div>
      </Card>

      {uploading.length > 0 && (
        <Card className="border-border/60 bg-card/80 p-6 shadow-card">
          <h3 className="text-sm font-semibold">Uploading</h3>
          <div className="mt-4 space-y-4">
            {uploading.map((u) => (
              <div key={u.name}>
                <div className="mb-1.5 flex items-center justify-between text-xs">
                  <span className="font-medium">{u.name}</span>
                  <span className="text-muted-foreground">{Math.round(u.pct)}%</span>
                </div>
                <Progress value={u.pct} className="h-2" />
              </div>
            ))}
          </div>
        </Card>
      )}

      <AnimatePresence>
        {pipelines.map((p) => (
          <motion.div
            key={p.name}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            <Card className="relative overflow-hidden border-border/60 bg-card/80 p-6 shadow-card">
              <div className="pointer-events-none absolute -right-16 -top-16 h-48 w-48 rounded-full bg-brand-gradient opacity-[0.08] blur-3xl" />
              <div className="mb-5 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-brand-gradient p-2 text-primary-foreground shadow-elegant">
                    <Zap className="h-4 w-4" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold">AI processing · {p.name}</div>
                    <div className="text-xs text-muted-foreground">
                      {p.stage === STAGES.length - 1 ? "Pipeline complete" : "Running enterprise AI pipeline…"}
                    </div>
                  </div>
                </div>
                <Badge className={p.stage === STAGES.length - 1 ? "bg-success/15 text-success" : "bg-brand-gradient text-primary-foreground"}>
                  {p.stage === STAGES.length - 1 ? "Ready" : `Stage ${p.stage + 1}/${STAGES.length}`}
                </Badge>
              </div>
              <div className="relative grid gap-2 md:grid-cols-4 lg:grid-cols-8">
                {STAGES.map((s, i) => {
                  const done = i < p.stage;
                  const active = i === p.stage;
                  const Icon = s.icon;
                  return (
                    <div key={s.key} className={`rounded-xl border p-3 text-xs transition-colors ${
                      done ? "border-success/40 bg-success/5" : active ? "border-primary/50 bg-primary/5" : "border-border/60 bg-background/60"
                    }`}>
                      <div className="flex items-center gap-2">
                        {done ? (
                          <CheckCircle2 className="h-4 w-4 text-success" />
                        ) : active ? (
                          <Loader2 className="h-4 w-4 animate-spin text-primary" />
                        ) : (
                          <Icon className="h-4 w-4 text-muted-foreground" />
                        )}
                        <span className={`font-semibold ${done ? "text-success" : active ? "text-foreground" : "text-muted-foreground"}`}>{s.label}</span>
                      </div>
                      <div className="mt-1 text-[10px] text-muted-foreground">{s.detail}</div>
                    </div>
                  );
                })}
              </div>
              {p.stage === STAGES.length - 1 && (
                <div className="mt-4 grid gap-3 sm:grid-cols-4">
                  {[
                    { l: "Rows processed", v: String(datasets.find(d => d.filename === p.name)?.rows ?? 0) },
                    { l: "Columns", v: String(datasets.find(d => d.filename === p.name)?.columns ?? 0) },
                    { l: "Status", v: "Ready" },
                  ].map((m) => (
                    <div key={m.l} className="rounded-lg border border-border/60 bg-background/60 p-3">
                      <div className="text-[10px] uppercase tracking-wider text-muted-foreground">{m.l}</div>
                      <div className="mt-1 text-sm font-semibold">{m.v}</div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </motion.div>
        ))}
      </AnimatePresence>

      <Card className="border-border/60 bg-card/80 p-6 shadow-card">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h3 className="text-base font-semibold">Recent uploads</h3>
            <p className="text-xs text-muted-foreground">Managed datasets and documents</p>
          </div>
        </div>
        <div className="mb-4 grid gap-3 md:grid-cols-2">
          <div className="rounded-lg border border-border/60 bg-background/50 p-3">
            <div className="text-sm font-semibold">Datasets</div>
            <div className="mt-2 text-xs text-muted-foreground">{datasets.length ? datasets.map((d) => d.filename).join(", ") : "No datasets uploaded yet."}</div>
          </div>
          <div className="rounded-lg border border-border/60 bg-background/50 p-3">
            <div className="text-sm font-semibold">Documents</div>
            <div className="mt-2 text-xs text-muted-foreground">{documents.length ? documents.map((d) => d.filename).join(", ") : "No documents uploaded yet."}</div>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border/60 text-left text-xs uppercase tracking-wider text-muted-foreground">
                <th className="py-2.5 pr-4">Name</th>
                <th className="py-2.5 pr-4">Type</th>
                <th className="py-2.5 pr-4">Rows</th>
                <th className="py-2.5 pr-4">Size</th>
                <th className="py-2.5 pr-4">Updated</th>
                <th className="py-2.5 pr-4">Status</th>
                <th className="py-2.5"></th>
              </tr>
            </thead>
            <tbody>
              {[...datasets.map((d) => ({ ...d, kind: "dataset" as const })), ...documents.map((d) => ({ ...d, kind: "document" as const }))]
                .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
                .map((item) => (
                  <tr key={`${item.kind}-${item.id}`} className="border-b border-border/40 last:border-0 hover:bg-muted/40">
                    <td className="py-3 pr-4">
                      <div className="flex items-center gap-2.5">
                        <div className="rounded-md bg-muted p-1.5 text-brand-gradient">
                          {item.kind === "document" ? <FileText className="h-4 w-4" /> : <File className="h-4 w-4" />}
                        </div>
                        <span className="font-medium">{item.filename}</span>
                      </div>
                    </td>
                    <td className="py-3 pr-4"><Badge variant="outline">{item.kind === "document" ? item.file_type?.toUpperCase() : "CSV"}</Badge></td>
                    <td className="py-3 pr-4 tabular-nums">{item.kind === "dataset" ? item.rows.toLocaleString() : "—"}</td>
                    <td className="py-3 pr-4">{item.kind === "dataset" ? `${item.columns} columns` : `${(item as { size_bytes: number }).size_bytes} bytes`}</td>
                    <td className="py-3 pr-4 text-muted-foreground">{item.created_at}</td>
                    <td className="py-3 pr-4"><Badge className="bg-success/15 text-success">Ready</Badge></td>
                    <td className="py-3">
                      <div className="flex justify-end gap-1">
                        <Button size="icon" variant="ghost"><Download className="h-4 w-4" /></Button>
                        <Button size="icon" variant="ghost"><Trash2 className="h-4 w-4" /></Button>
                        <Button size="icon" variant="ghost"><MoreHorizontal className="h-4 w-4" /></Button>
                      </div>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
