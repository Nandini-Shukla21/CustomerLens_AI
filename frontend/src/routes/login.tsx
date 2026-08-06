import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { useState } from "react";
import { ArrowRight, Eye, EyeOff, Lock, Mail, ShieldCheck, Sparkles } from "lucide-react";
import { Logo } from "@/components/brand/Logo";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import { platformApi } from "@/api/platform";

export const Route = createFileRoute("/login")({
  head: () => ({
    meta: [
      { title: "Sign in — CustomerLens AI" },
      { name: "description", content: "Sign in to CustomerLens AI, the enterprise customer intelligence platform." },
    ],
  }),
  component: LoginPage,
});

function LoginPage() {
  const navigate = useNavigate();
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);
  const [registering, setRegistering] = useState(false);

  const submit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    try {
      const form = new FormData(e.currentTarget);
      const result = registering ? await platformApi.register(String(form.get("name")), String(form.get("email")), String(form.get("password")), String(form.get("role"))) : await platformApi.login(String(form.get("email")), String(form.get("password")));
      sessionStorage.setItem("customerlens_token", result.access_token);
      sessionStorage.setItem("customerlens_user", JSON.stringify(result.user));
      toast.success(`Welcome back, ${result.user.name}.`);
      navigate({ to: "/home" });
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Unable to sign in.");
    } finally { setLoading(false); }
  };

  return (
    <div className="grid min-h-screen w-full lg:grid-cols-2">
      {/* Left */}
      <div className="relative hidden overflow-hidden bg-brand-gradient text-primary-foreground lg:flex">
        <div className="absolute inset-0 opacity-40">
          <div className="absolute -top-40 -left-20 h-[520px] w-[520px] rounded-full bg-white/25 blur-3xl animate-float-slow" />
          <div className="absolute bottom-0 right-0 h-[420px] w-[420px] rounded-full bg-cyan-300/40 blur-3xl animate-float-slow" style={{ animationDelay: "-5s" }} />
        </div>
        <div className="absolute inset-0 opacity-[0.18] mix-blend-overlay [background-image:radial-gradient(circle_at_1px_1px,white_1px,transparent_0)] [background-size:22px_22px]" />

        <div className="relative z-10 flex w-full flex-col justify-between p-12">
          <Logo />

          <div>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
              <div className="inline-flex items-center gap-2 rounded-full bg-white/15 px-3 py-1 text-xs font-medium backdrop-blur">
                <Sparkles className="h-3.5 w-3.5" /> Enterprise Customer Intelligence
              </div>
              <h1 className="mt-6 text-5xl font-bold leading-[1.05] tracking-tight">
                See beyond<br />the data.<br />
                <span className="opacity-80">Decide with intelligence.</span>
              </h1>
              <p className="mt-6 max-w-md text-base text-white/85">
                Unify ML, RAG, predictive analytics, and Customer 360 into a single AI workspace trusted by
                enterprise teams to power revenue-defining decisions.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.15 }}
              className="mt-10 grid grid-cols-3 gap-4"
            >
              {[
                { k: "12.4M", v: "Customers analyzed" },
                { k: "99.98%", v: "Platform uptime" },
                { k: "SOC 2", v: "Type II certified" },
              ].map((s) => (
                <div key={s.v} className="rounded-xl bg-white/10 p-4 backdrop-blur">
                  <div className="text-2xl font-bold">{s.k}</div>
                  <div className="mt-1 text-xs text-white/80">{s.v}</div>
                </div>
              ))}
            </motion.div>
          </div>

          <div className="flex items-center gap-2 text-xs text-white/80">
            <ShieldCheck className="h-4 w-4" /> SOC 2 · ISO 27001 · GDPR · HIPAA-ready
          </div>
        </div>
      </div>

      {/* Right */}
      <div className="relative flex items-center justify-center bg-background p-6 sm:p-10">
        <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
          <div className="absolute -top-24 right-0 h-72 w-72 rounded-full bg-brand-gradient opacity-[0.10] blur-3xl" />
        </div>

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="w-full max-w-md rounded-2xl border border-border/70 bg-card/80 p-8 shadow-elegant backdrop-blur-xl"
        >
          <div className="mb-6 flex items-center justify-between lg:hidden">
            <Logo />
          </div>
          <div className="mb-6">
            <h2 className="text-2xl font-bold tracking-tight">{registering ? "Create your account" : "Welcome back"}</h2>
            <p className="mt-1 text-sm text-muted-foreground">{registering ? "Set up your CustomerLens AI workspace." : "Sign in to your CustomerLens AI workspace."}</p>
          </div>

          <form onSubmit={submit} className="space-y-4">
            {registering && <><div className="space-y-1.5"><Label htmlFor="name">Full Name</Label><Input id="name" name="name" className="h-11" required /></div><div className="space-y-1.5"><Label htmlFor="role">Role</Label><select id="role" name="role" defaultValue="Viewer" className="h-11 w-full rounded-md border border-input bg-background px-3 text-sm"><option>Viewer</option><option>Analyst</option><option>Admin</option></select></div></>}
            <div className="space-y-1.5">
              <Label htmlFor="email">Work email</Label>
              <div className="relative">
                <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input id="email" name="email" type="email" className="h-11 pl-9" required />
              </div>
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <Label htmlFor="password">Password</Label>
                <button type="button" className="text-xs font-medium text-brand-gradient hover:underline">
                  Forgot password?
                </button>
              </div>
              <div className="relative">
                <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="password"
                  name="password"
                  type={show ? "text" : "password"}
                  className="h-11 pl-9 pr-10"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShow((v) => !v)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 rounded p-1.5 text-muted-foreground hover:bg-accent"
                  aria-label="Toggle password"
                >
                  {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Checkbox id="remember" defaultChecked />
              <Label htmlFor="remember" className="text-sm font-normal text-muted-foreground">
                Remember me for 30 days
              </Label>
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="group h-11 w-full bg-brand-gradient text-primary-foreground shadow-elegant hover:opacity-95"
            >
              {loading ? "Signing in…" : "Sign in"}
              <ArrowRight className="ml-1.5 h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </Button>

            <div className="relative py-1">
              <Separator />
              <span className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-card px-2 text-[11px] uppercase tracking-wider text-muted-foreground">
                or
              </span>
            </div>

            <div className="grid grid-cols-3 gap-2">
              <Button type="button" variant="outline" className="h-11 gap-2" aria-label="Google">
                <GoogleLogo />
              </Button>
              <Button type="button" variant="outline" className="h-11 gap-2" aria-label="Microsoft">
                <MicrosoftLogo />
              </Button>
              <Button type="button" variant="outline" className="h-11 gap-2" aria-label="GitHub">
                <GithubLogo />
              </Button>
            </div>

            <p className="pt-2 text-center text-xs text-muted-foreground">
              <button type="button" onClick={() => setRegistering(value => !value)} className="font-medium text-primary hover:underline">
                {registering ? "Already have an account? Sign in" : "New to CustomerLens? Create an account"}
              </button>
            </p>
          </form>
        </motion.div>
      </div>
    </div>
  );
}

function MicrosoftLogo() {
  return (
    <svg width="16" height="16" viewBox="0 0 23 23" aria-hidden="true">
      <rect width="10" height="10" fill="#F25022" />
      <rect x="12" width="10" height="10" fill="#7FBA00" />
      <rect y="12" width="10" height="10" fill="#00A4EF" />
      <rect x="12" y="12" width="10" height="10" fill="#FFB900" />
    </svg>
  );
}

function GoogleLogo() {
  return (
    <svg width="16" height="16" viewBox="0 0 48 48" aria-hidden="true">
      <path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.4 29.3 35.5 24 35.5c-6.4 0-11.5-5.1-11.5-11.5S17.6 12.5 24 12.5c2.9 0 5.6 1.1 7.6 2.9l5.7-5.7C33.6 6.2 29 4.5 24 4.5 13.2 4.5 4.5 13.2 4.5 24S13.2 43.5 24 43.5 43.5 34.8 43.5 24c0-1.2-.1-2.4-.3-3.5z" />
      <path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.7 15.6 19 12.5 24 12.5c2.9 0 5.6 1.1 7.6 2.9l5.7-5.7C33.6 6.2 29 4.5 24 4.5 16.3 4.5 9.7 8.9 6.3 14.7z" />
      <path fill="#4CAF50" d="M24 43.5c5 0 9.5-1.7 13-4.6l-6-5.1c-2 1.4-4.4 2.2-7 2.2-5.2 0-9.6-3.1-11.3-7.5l-6.6 5.1C9.6 39.4 16.2 43.5 24 43.5z" />
      <path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.2-2.2 4-4 5.3l6 5.1c-.4.4 6.7-4.9 6.7-14.4 0-1.2-.1-2.4-.4-3.5z" />
    </svg>
  );
}

function GithubLogo() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" fill="currentColor">
      <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.09 3.29 9.4 7.86 10.93.58.1.79-.25.79-.56v-2c-3.2.69-3.88-1.36-3.88-1.36-.53-1.34-1.29-1.7-1.29-1.7-1.05-.72.08-.71.08-.71 1.16.08 1.77 1.19 1.77 1.19 1.04 1.78 2.72 1.27 3.39.97.11-.75.41-1.27.74-1.56-2.55-.29-5.24-1.28-5.24-5.68 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.18 1.18a11 11 0 0 1 5.79 0c2.21-1.49 3.18-1.18 3.18-1.18.63 1.59.24 2.76.12 3.05.74.81 1.19 1.84 1.19 3.1 0 4.41-2.7 5.39-5.27 5.68.42.36.79 1.07.79 2.15v3.18c0 .31.21.67.8.56A11.51 11.51 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5z" />
    </svg>
  );
}
