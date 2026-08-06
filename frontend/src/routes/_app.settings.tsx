import { createFileRoute } from "@tanstack/react-router";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { PageHeader } from "@/components/ui/PageHeader";
import { Badge } from "@/components/ui/badge";
import { useTheme } from "@/components/theme-provider";

export const Route = createFileRoute("/_app/settings")({
  head: () => ({ meta: [{ title: "Settings — CustomerLens AI" }] }),
  component: SettingsPage,
});

function SettingsPage() {
  const { theme, setTheme } = useTheme();
  return (
    <div className="space-y-6">
      <PageHeader eyebrow="Settings" title="Workspace settings" description="Personalize theme, models, and system parameters." />

      <div className="grid gap-4 lg:grid-cols-2">
        <Card className="border-border/60 bg-card/80 p-6 shadow-card">
          <h3 className="text-base font-semibold">Appearance</h3>
          <div className="mt-4 space-y-4">
            <Row label="Theme">
              <Select value={theme} onValueChange={(v) => setTheme(v as "light"|"dark")}>
                <SelectTrigger className="w-40"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="light">Light</SelectItem>
                  <SelectItem value="dark">Dark</SelectItem>
                </SelectContent>
              </Select>
            </Row>
            <Row label="Language">
              <Select defaultValue="en">
                <SelectTrigger className="w-40"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="en">English (US)</SelectItem>
                  <SelectItem value="de">Deutsch</SelectItem>
                  <SelectItem value="fr">Français</SelectItem>
                </SelectContent>
              </Select>
            </Row>
            <Row label="Density">
              <Select defaultValue="comfortable">
                <SelectTrigger className="w-40"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="comfortable">Comfortable</SelectItem>
                  <SelectItem value="compact">Compact</SelectItem>
                </SelectContent>
              </Select>
            </Row>
          </div>
        </Card>

        <Card className="border-border/60 bg-card/80 p-6 shadow-card">
          <h3 className="text-base font-semibold">Notifications</h3>
          <div className="mt-4 space-y-4">
            {[
              "New AI insights",
              "Prediction refresh complete",
              "Upload processing complete",
              "System alerts",
            ].map((n) => (
              <Row key={n} label={n}><Switch defaultChecked /></Row>
            ))}
          </div>
        </Card>

        <Card className="border-border/60 bg-card/80 p-6 shadow-card">
          <h3 className="text-base font-semibold">AI configuration</h3>
          <div className="mt-4 space-y-5">
            <Row label="LLM model">
              <Select defaultValue="gpte">
                <SelectTrigger className="w-56"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="gpte">GPT-Enterprise · v4.2</SelectItem>
                  <SelectItem value="claude">Claude Sonnet · 4.5</SelectItem>
                  <SelectItem value="llama">Llama 4 Enterprise</SelectItem>
                </SelectContent>
              </Select>
            </Row>
            <Row label="Embedding model">
              <Select defaultValue="e3">
                <SelectTrigger className="w-56"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="e3">text-embedding-3-large</SelectItem>
                  <SelectItem value="bge">bge-m3</SelectItem>
                </SelectContent>
              </Select>
            </Row>
            <Row label="Chunk size">
              <div className="flex items-center gap-3">
                <Slider defaultValue={[512]} min={128} max={2048} step={64} className="w-48" />
                <span className="text-sm tabular-nums">512</span>
              </div>
            </Row>
            <Row label="Top-K retrieval">
              <div className="flex items-center gap-3">
                <Slider defaultValue={[8]} min={1} max={20} step={1} className="w-48" />
                <span className="text-sm tabular-nums">8</span>
              </div>
            </Row>
          </div>
        </Card>

        <Card className="border-border/60 bg-card/80 p-6 shadow-card">
          <h3 className="text-base font-semibold">System</h3>
          <div className="mt-4 space-y-3 text-sm">
            <Row label="API health"><Badge className="bg-success/15 text-success">Operational</Badge></Row>
            <Row label="Region"><span className="text-muted-foreground">eu-west-1 · London</span></Row>
            <Row label="Platform version"><span className="text-muted-foreground">CustomerLens 2026.11.2</span></Row>
            <Row label="Compliance"><span className="text-muted-foreground">SOC 2 · ISO 27001 · GDPR</span></Row>
          </div>
        </Card>
      </div>
    </div>
  );
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <Label className="text-sm font-normal text-muted-foreground">{label}</Label>
      {children}
    </div>
  );
}
