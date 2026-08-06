import { Link, useRouterState } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";

export function FloatingAIButton() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  if (pathname.startsWith("/copilot") || pathname === "/login" || pathname === "/") return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.7, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ delay: 0.4, type: "spring", stiffness: 220, damping: 18 }}
      className="fixed bottom-6 right-6 z-40"
    >
      <Link to="/copilot" aria-label="Ask Copilot">
        <div className="group relative">
          <span className="absolute inset-0 animate-ping rounded-full bg-brand-gradient opacity-30" />
          <span className="absolute -inset-1 rounded-full bg-brand-gradient opacity-40 blur-xl transition-opacity group-hover:opacity-70" />
          <div className="relative flex items-center gap-2 rounded-full bg-brand-gradient px-4 py-3 text-primary-foreground shadow-elegant transition-transform hover:scale-105">
            <Sparkles className="h-5 w-5" />
            <span className="pr-1 text-sm font-semibold">Ask Copilot</span>
          </div>
        </div>
      </Link>
    </motion.div>
  );
}
