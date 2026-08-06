import { createFileRoute } from "@tanstack/react-router";
import { motion } from "framer-motion";
import {
  ArrowDown,
  BrainCircuit,
  CheckCircle2,
  Database,
  FileText,
  LayoutDashboard,
  MessageSquare,
  Sparkles,
  Upload,
  Workflow as WorkflowIcon,
  Zap,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageHeader } from "@/components/ui/PageHeader";

export const Route = createFileRoute("/_app/workflow")({
  head: () => ({ meta: [{ title: "AI Workflow — CustomerLens AI" }] }),
  component: WorkflowPage,
});

const steps = [
  { icon: Upload, title: "Upload Data", desc: "CSV, Parquet, Excel, JSON — plus PDF, DOCX, TXT.", metric: "1.24M rows", status: "Complete" },
  { icon: Zap, title: "Clean Data", desc: "Missing values, duplicates, type coercion.", metric: "99.4% quality", status: "Complete" },
  { icon: FileText, title: "Process Documents", desc: "Chunking, deduplication, semantic segmentation.", metric: "12,914 chunks", status: "Complete" },
  { icon: BrainCircuit, title: "Generate Embeddings", desc: "text-embedding-3-large, 3,072-dim vectors.", metric: "12,914 vectors", status: "Complete" },
  { icon: Database, title: "Vector Database", desc: "Persisted to managed pgvector cluster.", metric: "3 shards · HA", status: "Complete" },
  { icon: Sparkles, title: "Retrieve Context", desc: "Hybrid search with reranking (top-K = 8).", metric: "128ms p95", status: "Live" },
  { icon: BrainCircuit, title: "LLM Reasoning", desc: "GPT-Enterprise v4.2 · grounded on retrieved context.", metric: "1.42s avg", status: "Live" },
  { icon: MessageSquare, title: "AI Response", desc: "Cited, confidence-scored, action-oriented.", metric: "94% confidence", status: "Live" },
  { icon: LayoutDashboard, title: "Interactive Dashboard", desc: "Auto-generated charts and executive summaries.", metric: "4 insights ready", status: "Live" },
];

function WorkflowPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="AI Workflow"
        title="From raw data to a decision"
        description="A transparent pipeline every stakeholder can inspect — upload, clean, embed, retrieve, reason, decide."
      />

      <div className="relative mx-auto max-w-3xl space-y-3">
        {steps.map((s, i) => (
          <motion.div
            key={s.title}
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-60px" }}
            transition={{ duration: 0.4, delay: i * 0.06 }}
          >
            <Card className="relative overflow-hidden border-border/60 bg-card/70 p-5 shadow-card backdrop-blur-sm">
              <div className="pointer-events-none absolute -right-8 -top-8 h-24 w-24 rounded-full bg-brand-gradient opacity-[0.08] blur-2xl" />
              <div className="flex items-center gap-4">
                <div className="relative">
                  <div className="rounded-xl bg-brand-gradient p-3 text-primary-foreground shadow-elegant">
                    <s.icon className="h-5 w-5" />
                  </div>
                  {s.status === "Live" && (
                    <span className="absolute -right-1 -top-1 h-3 w-3 rounded-full bg-success ring-2 ring-background">
                      <span className="absolute inset-0 animate-ping rounded-full bg-success/60" />
                    </span>
                  )}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <div className="text-xs font-bold tracking-widest text-muted-foreground">
                      {String(i + 1).padStart(2, "0")}
                    </div>
                    <div className="text-base font-semibold">{s.title}</div>
                    <Badge variant="outline" className="ml-auto gap-1 text-[10px]">
                      <CheckCircle2 className="h-3 w-3 text-success" /> {s.status}
                    </Badge>
                  </div>
                  <div className="mt-1 text-sm text-muted-foreground">{s.desc}</div>
                  <div className="mt-2 text-xs font-semibold text-brand-gradient">{s.metric}</div>
                </div>
              </div>
            </Card>
            {i < steps.length - 1 && (
              <div className="flex justify-center py-1">
                <motion.div
                  initial={{ opacity: 0 }}
                  whileInView={{ opacity: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.06 + 0.2 }}
                >
                  <ArrowDown className="h-4 w-4 text-muted-foreground" />
                </motion.div>
              </div>
            )}
          </motion.div>
        ))}
      </div>

      <Card className="mx-auto max-w-3xl border-border/60 bg-brand-gradient/5 p-6 text-center shadow-card">
        <WorkflowIcon className="mx-auto h-6 w-6 text-brand-gradient" />
        <div className="mt-2 text-base font-semibold">Pipeline healthy · Last run 4m ago</div>
        <p className="mt-1 text-sm text-muted-foreground">All stages meeting SLA. Next scheduled refresh in 26 minutes.</p>
      </Card>
    </div>
  );
}
