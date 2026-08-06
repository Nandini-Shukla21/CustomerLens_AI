import { createFileRoute } from "@tanstack/react-router";
import { BookOpen, LifeBuoy, MessageSquare, Search, Sparkles } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/PageHeader";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";

export const Route = createFileRoute("/_app/help")({
  head: () => ({ meta: [{ title: "Help & Documentation — CustomerLens AI" }] }),
  component: HelpPage,
});

const faqs = [
  { q: "How do I connect a data warehouse?", a: "Go to Upload Center → Connect Snowflake / S3 / BigQuery. Grant read access via the guided flow and CustomerLens will index metadata automatically." },
  { q: "Which file formats are supported?", a: "CSV, Excel, JSON, Parquet for datasets; PDF, DOCX, TXT for documents (indexed into the RAG knowledge base)." },
  { q: "How does Copilot cite sources?", a: "Every Copilot answer surfaces the datasets and documents it retrieved, along with a confidence score and execution time." },
  { q: "Is my data used to train models?", a: "Never. Your data stays in your tenant. Enterprise workspaces use isolated embeddings and per-tenant retrieval." },
  { q: "How are permissions managed?", a: "Role-based access control with SSO (SAML/OIDC) and SCIM provisioning. Column- and row-level policies enforce dataset-level scopes." },
];

function HelpPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Help & Documentation"
        title="How can we help?"
        description="Guides, API references, and enterprise support — 24/7."
      />

      <Card className="relative overflow-hidden border-border/60 bg-card/80 p-8 shadow-card">
        <div className="pointer-events-none absolute inset-0 bg-brand-gradient opacity-[0.06]" />
        <div className="relative mx-auto max-w-2xl">
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input placeholder="Search the docs, guides, and API reference…" className="h-12 pl-10" />
          </div>
          <div className="mt-3 flex flex-wrap justify-center gap-2 text-xs text-muted-foreground">
            {["Getting started","Copilot","RAG","Predictions","Security"].map((t) => (
              <span key={t} className="rounded-full border border-border/60 bg-background px-2.5 py-0.5">{t}</span>
            ))}
          </div>
        </div>
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        {[
          { i: BookOpen, t: "Documentation", d: "Guides, tutorials, and best practices for every module." },
          { i: Sparkles, t: "Copilot recipes", d: "Prompt patterns for revenue, churn, complaints, and more." },
          { i: LifeBuoy, t: "Enterprise support", d: "24/7 support with a dedicated CSM and SLAs." },
        ].map((t) => (
          <Card key={t.t} className="border-border/60 bg-card/80 p-6 shadow-card">
            <div className="rounded-lg bg-brand-gradient p-2 text-primary-foreground shadow-elegant inline-flex"><t.i className="h-4 w-4" /></div>
            <div className="mt-3 text-base font-semibold">{t.t}</div>
            <div className="mt-1 text-sm text-muted-foreground">{t.d}</div>
            <Button variant="outline" size="sm" className="mt-4">Open</Button>
          </Card>
        ))}
      </div>

      <Card className="border-border/60 bg-card/80 p-6 shadow-card">
        <h3 className="text-base font-semibold">Frequently asked questions</h3>
        <Accordion type="single" collapsible className="mt-3">
          {faqs.map((f, i) => (
            <AccordionItem key={i} value={`i${i}`}>
              <AccordionTrigger className="text-sm">{f.q}</AccordionTrigger>
              <AccordionContent className="text-sm text-muted-foreground">{f.a}</AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </Card>

      <Card className="flex flex-col items-center justify-between gap-4 border-border/60 bg-brand-gradient p-6 text-primary-foreground shadow-elegant md:flex-row">
        <div className="flex items-center gap-3">
          <MessageSquare className="h-6 w-6" />
          <div>
            <div className="font-semibold">Still need help?</div>
            <div className="text-sm opacity-90">Chat with our enterprise support team.</div>
          </div>
        </div>
        <Button variant="secondary" className="bg-white text-primary hover:bg-white/95">Contact support</Button>
      </Card>
    </div>
  );
}
