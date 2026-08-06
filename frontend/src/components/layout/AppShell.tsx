import { Link, Outlet, useRouterState, useNavigate } from "@tanstack/react-router";
import {
  Bell,
  ChevronsLeft,
  ChevronsRight,
  HelpCircle,
  LayoutDashboard,
  LineChart,
  MessageSquare,
  Moon,
  Search,
  Settings,
  Sparkles,
  Sun,
  Upload,
  Users,
  Database,
  FileText,
  BrainCircuit,
  TrendingUp,
  Home as HomeIcon,
  BellDot,
  UserCircle2,
  LogOut,
  Command as CommandIcon,
  Workflow as WorkflowIcon,
} from "lucide-react";
import { FloatingAIButton } from "@/components/ui/FloatingAIButton";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "@/components/ui/command";
import { useEffect } from "react";
import { useState, type ComponentType } from "react";
import { useQuery } from "@tanstack/react-query";
import { platformApi } from "@/api/platform";
import { Logo, LogoMark } from "@/components/brand/Logo";
import { Button } from "@/components/ui/button";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useTheme } from "@/components/theme-provider";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

type NavItem = { to: string; label: string; icon: ComponentType<{ className?: string }>; badge?: string };

const NAV: { section: string; items: NavItem[] }[] = [
  {
    section: "Overview",
    items: [
      { to: "/home", label: "Home", icon: HomeIcon },
      { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    ],
  },
  {
    section: "Data",
    items: [
      { to: "/upload", label: "Upload Center", icon: Upload },
      { to: "/datasets", label: "Dataset Explorer", icon: Database },
      { to: "/workflow", label: "AI Workflow", icon: WorkflowIcon },
    ],
  },
  {
    section: "Intelligence",
    items: [
      { to: "/copilot", label: "AI Copilot", icon: Sparkles, badge: "New" },
      { to: "/customer-360", label: "Customer 360", icon: Users },
      { to: "/analytics", label: "Analytics", icon: LineChart },
      { to: "/insights", label: "AI Insights", icon: BrainCircuit },
      { to: "/predictions", label: "Predictions", icon: TrendingUp },
      { to: "/reports", label: "Reports", icon: FileText },
    ],
  },
  {
    section: "Workspace",
    items: [
      { to: "/notifications", label: "Notifications", icon: Bell },
      { to: "/settings", label: "Settings", icon: Settings },
      { to: "/help", label: "Help & Docs", icon: HelpCircle },
    ],
  },
];

export function AppShell() {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [cmdOpen, setCmdOpen] = useState(false);
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const { theme, toggle } = useTheme();
  const navigate = useNavigate();
  const { data: user } = useQuery({ queryKey: ["current-user"], queryFn: platformApi.me, retry: false });
  const displayName = user?.name || user?.email || "Account";

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setCmdOpen((v) => !v);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const go = (to: string) => {
    setCmdOpen(false);
    navigate({ to });
  };

  return (
    <div className="relative min-h-screen w-full bg-background text-foreground">
      {/* Ambient gradient blobs */}
      <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute -top-40 -left-32 h-[420px] w-[420px] rounded-full bg-brand-gradient opacity-[0.14] blur-3xl animate-float-slow" />
        <div className="absolute top-1/3 -right-40 h-[520px] w-[520px] rounded-full bg-brand-gradient opacity-[0.10] blur-3xl animate-float-slow" style={{ animationDelay: "-6s" }} />
      </div>

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 flex flex-col border-r border-sidebar-border bg-sidebar/80 backdrop-blur-xl transition-[width] duration-300",
          collapsed ? "w-[76px]" : "w-[264px]",
          mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0",
        )}
      >
        <div className="flex h-16 shrink-0 items-center justify-between px-4">
          {collapsed ? <LogoMark /> : <Logo />}
          <button
            aria-label="Toggle sidebar"
            onClick={() => setCollapsed((c) => !c)}
            className="hidden rounded-md p-1.5 text-muted-foreground hover:bg-sidebar-accent lg:inline-flex"
          >
            {collapsed ? <ChevronsRight className="h-4 w-4" /> : <ChevronsLeft className="h-4 w-4" />}
          </button>
        </div>

        <nav className="flex-1 space-y-6 overflow-y-auto px-3 pb-6">
          {NAV.map((group) => (
            <div key={group.section}>
              {!collapsed && (
                <div className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-[0.14em] text-muted-foreground/70">
                  {group.section}
                </div>
              )}
              <ul className="space-y-0.5">
                {group.items.map((item) => {
                  const active =
                    item.to === "/" ? pathname === "/" : pathname === item.to || pathname.startsWith(item.to + "/");
                  const Icon = item.icon;
                  return (
                    <li key={item.to}>
                      <Link
                        to={item.to}
                        onClick={() => setMobileOpen(false)}
                        className={cn(
                          "group relative flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                          active
                            ? "bg-sidebar-accent text-sidebar-accent-foreground"
                            : "text-sidebar-foreground/80 hover:bg-sidebar-accent/60 hover:text-sidebar-foreground",
                        )}
                      >
                        {active && (
                          <motion.span
                            layoutId="active-pill"
                            className="absolute inset-y-1 left-0 w-1 rounded-r bg-brand-gradient"
                          />
                        )}
                        <Icon className={cn("h-[18px] w-[18px] shrink-0", active && "text-primary")} />
                        {!collapsed && <span className="flex-1 truncate">{item.label}</span>}
                        {!collapsed && item.badge && (
                          <Badge className="border-0 bg-brand-gradient text-[10px] text-primary-foreground">
                            {item.badge}
                          </Badge>
                        )}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </nav>

        {!collapsed && (
          <div className="mx-3 mb-4 rounded-xl border border-sidebar-border bg-brand-gradient p-4 text-primary-foreground shadow-elegant">
            <Sparkles className="h-5 w-5" />
            <div className="mt-2 text-sm font-semibold">Upgrade to Enterprise</div>
            <div className="mt-1 text-xs opacity-90">Unlimited seats, private RAG, dedicated SLAs.</div>
            <Button size="sm" variant="secondary" className="mt-3 h-8 w-full bg-white/95 text-primary hover:bg-white">
              Contact Sales
            </Button>
          </div>
        )}
      </aside>

      {/* Main */}
      <div className={cn("min-h-screen transition-[padding] duration-300", collapsed ? "lg:pl-[76px]" : "lg:pl-[264px]")}>
        {/* Topbar */}
        <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b border-border/60 bg-background/70 px-4 backdrop-blur-xl md:px-6">
          <button
            className="rounded-md p-2 text-muted-foreground hover:bg-accent lg:hidden"
            onClick={() => setMobileOpen((v) => !v)}
            aria-label="Open menu"
          >
            <LayoutDashboard className="h-5 w-5" />
          </button>

          <button
            onClick={() => setCmdOpen(true)}
            className="relative hidden max-w-xl flex-1 items-center rounded-lg border border-border/70 bg-muted/40 pl-9 pr-16 text-left text-sm text-muted-foreground transition-colors hover:bg-muted/60 md:flex md:h-10"
          >
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2" />
            <span className="truncate">Search customers, datasets, insights, docs…</span>
            <kbd className="absolute right-3 top-1/2 hidden -translate-y-1/2 items-center gap-1 rounded border border-border/60 bg-background px-1.5 py-0.5 text-[10px] font-semibold md:inline-flex">
              <CommandIcon className="h-3 w-3" /> K
            </kbd>
          </button>

          <div className="ml-auto flex items-center gap-1.5">
            <Button variant="ghost" size="icon" onClick={toggle} aria-label="Toggle theme">
              {theme === "dark" ? <Sun className="h-[18px] w-[18px]" /> : <Moon className="h-[18px] w-[18px]" />}
            </Button>
            <Link to="/copilot">
              <Button variant="ghost" size="icon" aria-label="Copilot">
                <MessageSquare className="h-[18px] w-[18px]" />
              </Button>
            </Link>
            <Link to="/notifications">
              <Button variant="ghost" size="icon" aria-label="Notifications" className="relative">
                <BellDot className="h-[18px] w-[18px]" />
                <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-brand-gradient" />
              </Button>
            </Link>
            <Link to="/settings" className="hidden md:inline-flex">
              <Button variant="ghost" size="icon" aria-label="Settings">
                <Settings className="h-[18px] w-[18px]" />
              </Button>
            </Link>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="ml-1 flex items-center gap-2 rounded-full border border-border/60 p-0.5 pr-3 transition-colors hover:bg-accent">
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className="bg-brand-gradient text-xs font-semibold text-primary-foreground">
                      {displayName.split(" ").map((part: string) => part[0]).join("").slice(0, 2).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div className="hidden text-left text-xs leading-tight md:block">
                    <div className="font-semibold">{displayName}</div>
                    <div className="text-muted-foreground">{user?.role || "Account"}</div>
                  </div>
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>My account</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link to="/profile"><UserCircle2 className="mr-2 h-4 w-4" />Profile</Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link to="/settings"><Settings className="mr-2 h-4 w-4" />Settings</Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link to="/help"><HelpCircle className="mr-2 h-4 w-4" />Help</Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link to="/login"><LogOut className="mr-2 h-4 w-4" />Sign out</Link>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        <AnimatePresence mode="wait">
          <motion.main
            key={pathname}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.25, ease: "easeOut" }}
            className="px-4 py-6 md:px-8 md:py-8"
          >
            <Outlet />
          </motion.main>
        </AnimatePresence>
      </div>

      {mobileOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/40 backdrop-blur-sm lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <FloatingAIButton />

      <CommandDialog open={cmdOpen} onOpenChange={setCmdOpen}>
        <CommandInput placeholder="Type a command or search…" />
        <CommandList>
          <CommandEmpty>No results found.</CommandEmpty>
          <CommandGroup heading="Navigation">
            {NAV.flatMap((g) => g.items).map((i) => (
              <CommandItem key={i.to} onSelect={() => go(i.to)}>
                <i.icon className="mr-2 h-4 w-4" /> {i.label}
              </CommandItem>
            ))}
          </CommandGroup>
          <CommandSeparator />
          <CommandGroup heading="Actions">
            <CommandItem onSelect={() => go("/copilot")}><Sparkles className="mr-2 h-4 w-4" /> Ask Copilot</CommandItem>
            <CommandItem onSelect={() => go("/upload")}><Upload className="mr-2 h-4 w-4" /> Upload dataset</CommandItem>
            <CommandItem onSelect={() => go("/reports")}><FileText className="mr-2 h-4 w-4" /> Generate report</CommandItem>
          </CommandGroup>
        </CommandList>
      </CommandDialog>
    </div>
  );
}
