import { ArrowDownRight, ArrowUpRight, type LucideIcon } from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { Card } from "@/components/ui/card";
import { Sparkline } from "@/components/charts/Sparkline";

export function StatCard({
  label,
  value,
  delta,
  trend,
  icon: Icon,
  data,
  accent = "brand",
}: {
  label: string;
  value: string;
  delta?: string;
  trend?: "up" | "down";
  icon: LucideIcon;
  data?: number[];
  accent?: "brand" | "cyan" | "violet" | "success" | "warning";
}) {
  const accentClass =
    accent === "success"
      ? "text-success"
      : accent === "warning"
        ? "text-warning"
        : "text-brand-gradient";

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }}>
      <Card className="relative overflow-hidden border-border/60 bg-card/80 p-5 shadow-card backdrop-blur-sm transition-all hover:-translate-y-0.5 hover:shadow-elegant">
        <div className="pointer-events-none absolute -right-8 -top-8 h-28 w-28 rounded-full bg-brand-gradient opacity-[0.08] blur-2xl" />
        <div className="flex items-start justify-between">
          <div className="min-w-0">
            <div className="text-xs font-medium uppercase tracking-wider text-muted-foreground">{label}</div>
            <div className="mt-2 text-2xl font-bold tracking-tight md:text-[26px]">{value}</div>
            {delta && (
              <div className="mt-1 flex items-center gap-1 text-xs">
                {trend === "down" ? (
                  <ArrowDownRight className="h-3.5 w-3.5 text-destructive" />
                ) : (
                  <ArrowUpRight className="h-3.5 w-3.5 text-success" />
                )}
                <span className={cn(trend === "down" ? "text-destructive" : "text-success", "font-semibold")}>
                  {delta}
                </span>
                <span className="text-muted-foreground">vs last period</span>
              </div>
            )}
          </div>
          <div className={cn("rounded-xl bg-muted/60 p-2.5 ring-1 ring-border/60", accentClass)}>
            <Icon className="h-5 w-5" />
          </div>
        </div>
        {data && (
          <div className="mt-4 h-12">
            <Sparkline data={data} trend={trend} />
          </div>
        )}
      </Card>
    </motion.div>
  );
}
