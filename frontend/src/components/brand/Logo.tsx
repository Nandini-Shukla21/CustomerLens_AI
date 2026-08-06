import { cn } from "@/lib/utils";

/**
 * CustomerLens mark — an abstract "CL" monogram formed by a customer network:
 * an outer arc (the "C" — reach) and three connected nodes (the "L" spine — relationships).
 * No robots, no sparkles, no brain — pure enterprise geometry.
 */
export function LogoMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 40 40" className={cn("h-8 w-8", className)} aria-hidden="true">
      <defs>
        <linearGradient id="cl-grad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#6366F1" />
          <stop offset="55%" stopColor="#8B5CF6" />
          <stop offset="100%" stopColor="#22D3EE" />
        </linearGradient>
      </defs>
      {/* Outer "C" arc — 270deg */}
      <path
        d="M32 11a13 13 0 1 0 0 18"
        fill="none"
        stroke="url(#cl-grad)"
        strokeWidth="3"
        strokeLinecap="round"
      />
      {/* Connection lines between nodes (network spine forming the "L") */}
      <path
        d="M14 14 L14 26 L28 26"
        fill="none"
        stroke="url(#cl-grad)"
        strokeWidth="2"
        strokeLinecap="round"
        opacity="0.9"
      />
      {/* Nodes */}
      <circle cx="14" cy="14" r="2.6" fill="url(#cl-grad)" />
      <circle cx="14" cy="26" r="2.6" fill="url(#cl-grad)" />
      <circle cx="28" cy="26" r="2.6" fill="url(#cl-grad)" />
    </svg>
  );
}

export function Logo({ className, compact = false }: { className?: string; compact?: boolean }) {
  return (
    <div className={cn("flex items-center gap-2.5", className)}>
      <LogoMark />
      {!compact && (
        <div className="leading-none">
          <div className="text-[15px] font-semibold tracking-tight">
            Customer<span className="text-brand-gradient font-bold">Lens</span>
          </div>
          <div className="mt-1 text-[9px] uppercase tracking-[0.22em] text-muted-foreground">
            Customer Intelligence
          </div>
        </div>
      )}
    </div>
  );
}
