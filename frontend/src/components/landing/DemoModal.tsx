import { motion, AnimatePresence } from "framer-motion";
import { Play, X, Bell } from "lucide-react";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

export function DemoModal({ open, onClose, plan }: { open: boolean; onClose: () => void; plan?: string }) {
  const [email, setEmail] = useState("");

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    if (open) window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 p-4 backdrop-blur-md"
          onClick={onClose}
        >
          <motion.div
            initial={{ opacity: 0, y: 24, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 12, scale: 0.98 }}
            transition={{ type: "spring", damping: 24, stiffness: 260 }}
            onClick={(e) => e.stopPropagation()}
            className="relative w-full max-w-2xl overflow-hidden rounded-2xl border border-white/10 bg-[#0B0E1A] shadow-2xl"
          >
            <div className="absolute inset-0 bg-brand-gradient opacity-[0.08]" />
            <div className="pointer-events-none absolute -top-24 -right-24 h-72 w-72 rounded-full bg-brand-gradient opacity-30 blur-3xl" />

            <button
              onClick={onClose}
              className="absolute right-4 top-4 z-10 rounded-lg p-1.5 text-white/70 transition hover:bg-white/10 hover:text-white"
              aria-label="Close"
            >
              <X className="h-4 w-4" />
            </button>

            <div className="relative p-8 md:p-10">
              <div className="text-xs font-semibold uppercase tracking-[0.24em] text-brand-gradient">
                Live Walkthrough
              </div>
              <h3 className="mt-2 text-2xl font-bold tracking-tight text-white md:text-3xl">
                CustomerLens Product Walkthrough
              </h3>
              {plan && (
                <div className="mt-3 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-white/80">
                  Interested in <span className="font-semibold text-white">{plan}</span>
                </div>
              )}

              {/* Player mock */}
              <div className="relative mt-6 aspect-video overflow-hidden rounded-xl border border-white/10 bg-black/40">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(139,92,246,0.25),transparent_60%)]" />
                <div className="absolute inset-0 flex flex-col items-center justify-center gap-4">
                  <motion.div
                    animate={{ scale: [1, 1.08, 1] }}
                    transition={{ duration: 2.2, repeat: Infinity, ease: "easeInOut" }}
                    className="relative"
                  >
                    <div className="absolute inset-0 rounded-full bg-brand-gradient blur-2xl opacity-60" />
                    <div className="relative flex h-20 w-20 items-center justify-center rounded-full bg-brand-gradient shadow-2xl">
                      <Play className="h-8 w-8 text-white" fill="currentColor" />
                    </div>
                  </motion.div>
                  <div className="text-sm font-semibold uppercase tracking-[0.2em] text-white/80">
                    Product Demo Coming Soon
                  </div>
                </div>
              </div>

              <p className="mt-6 text-sm leading-relaxed text-white/70">
                Our interactive product walkthrough is currently being prepared. Discover how CustomerLens
                transforms customer intelligence into actionable business decisions.
              </p>

              <div className="mt-6 flex flex-col gap-3 sm:flex-row">
                <div className="relative flex-1">
                  <Bell className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/40" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Work email"
                    className="h-11 w-full rounded-lg border border-white/10 bg-white/5 pl-9 pr-3 text-sm text-white placeholder:text-white/40 focus:border-white/20 focus:outline-none focus:ring-2 focus:ring-indigo-500/40"
                  />
                </div>
                <Button
                  onClick={() => {
                    if (!email) return toast.error("Enter your work email");
                    toast.success("You're on the list — we'll notify you at launch.");
                    setEmail("");
                    onClose();
                  }}
                  className="h-11 bg-brand-gradient px-6 text-primary-foreground shadow-elegant hover:opacity-95"
                >
                  Notify Me
                </Button>
                <Button
                  onClick={onClose}
                  variant="outline"
                  className="h-11 border-white/15 bg-white/5 text-white hover:bg-white/10"
                >
                  Close
                </Button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
