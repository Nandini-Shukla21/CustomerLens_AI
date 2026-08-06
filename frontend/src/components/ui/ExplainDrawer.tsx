import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { BookOpen, BrainCircuit, FileText, Sparkles, Target } from "lucide-react";
import type { ReactNode } from "react";

export type Explanation = {
  title: string;
  summary: string;
  confidence: number;
  features: { name: string; weight: number }[];
  evidence: string[];
  sources: string[];
  action: string;
};

export function ExplainDrawer({ children, explanation }: { children: ReactNode; explanation: Explanation }) {
  const e = explanation;
  return (
    <Sheet>
      <SheetTrigger asChild>{children}</SheetTrigger>
      <SheetContent side="right" className="w-full overflow-y-auto sm:max-w-lg">
        <SheetHeader>
          <div className="flex items-center gap-2">
            <div className="rounded-lg bg-brand-gradient p-2 text-primary-foreground shadow-elegant">
              <BrainCircuit className="h-4 w-4" />
            </div>
            <div>
              <div className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Explainable AI</div>
              <SheetTitle className="text-base">{e.title}</SheetTitle>
            </div>
          </div>
          <SheetDescription className="mt-2 text-sm">{e.summary}</SheetDescription>
        </SheetHeader>

        <div className="mt-6 space-y-6">
          <section>
            <div className="mb-1.5 flex items-center justify-between text-xs">
              <span className="flex items-center gap-1.5 text-muted-foreground"><Sparkles className="h-3.5 w-3.5" /> Confidence</span>
              <span className="font-semibold">{(e.confidence * 100).toFixed(0)}%</span>
            </div>
            <Progress value={e.confidence * 100} className="h-1.5" />
          </section>

          <section>
            <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">Feature importance</h4>
            <ul className="space-y-2">
              {e.features.map((f) => (
                <li key={f.name}>
                  <div className="mb-1 flex items-center justify-between text-xs">
                    <span>{f.name}</span>
                    <span className="text-muted-foreground tabular-nums">{(f.weight * 100).toFixed(0)}%</span>
                  </div>
                  <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
                    <div className="h-full bg-brand-gradient" style={{ width: `${f.weight * 100}%` }} />
                  </div>
                </li>
              ))}
            </ul>
          </section>

          <section>
            <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">Evidence used</h4>
            <ul className="space-y-2 text-sm">
              {e.evidence.map((ev, i) => (
                <li key={i} className="flex items-start gap-2 rounded-lg border border-border/60 bg-background/60 p-3">
                  <BookOpen className="mt-0.5 h-4 w-4 shrink-0 text-brand-gradient" />
                  <span>{ev}</span>
                </li>
              ))}
            </ul>
          </section>

          <section>
            <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">Retrieved sources</h4>
            <div className="flex flex-wrap gap-2">
              {e.sources.map((s) => (
                <Badge key={s} variant="outline" className="gap-1"><FileText className="h-3 w-3" />{s}</Badge>
              ))}
            </div>
          </section>

          <section className="rounded-xl border border-border/60 bg-brand-gradient/5 p-4">
            <div className="mb-1 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-brand-gradient">
              <Target className="h-3.5 w-3.5" /> Recommended action
            </div>
            <p className="text-sm">{e.action}</p>
            <div className="mt-3 flex gap-2">
              <Button size="sm" className="bg-brand-gradient text-primary-foreground shadow-elegant hover:opacity-95">Apply</Button>
              <Button size="sm" variant="outline">Assign to team</Button>
            </div>
          </section>
        </div>
      </SheetContent>
    </Sheet>
  );
}
