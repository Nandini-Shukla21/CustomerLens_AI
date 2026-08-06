import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { PageHeader } from "@/components/ui/PageHeader";
import { platformApi, type Dataset } from "@/api/platform";

export const Route = createFileRoute("/_app/datasets")({ component: DatasetsPage });
function DatasetsPage() {
  const { data: datasets = [] } = useQuery({ queryKey: ["datasets"], queryFn: platformApi.datasets });
  const [selected, setSelected] = useState<Dataset | undefined>(); const [q, setQ] = useState("");
  useEffect(() => { if (!selected && datasets[0]) setSelected(datasets[0]); }, [datasets, selected]);
  const preview = useQuery({ queryKey: ["dataset-preview", selected?.id, q], queryFn: () => platformApi.datasetPreview(selected!.id, 0, q), enabled: !!selected });
  const columns = useQuery({ queryKey: ["dataset-columns", selected?.id], queryFn: () => platformApi.datasetColumns(selected!.id), enabled: !!selected });
  return <div className="space-y-6"><PageHeader eyebrow="Dataset Explorer" title={selected?.filename ?? "Uploaded datasets"} description={selected ? `${selected.rows.toLocaleString()} rows · ${selected.columns} columns` : "Upload a dataset to begin."}/>
    <div className="grid gap-3 md:grid-cols-3">{datasets.map(d => <button key={d.id} onClick={() => setSelected(d)} className={`rounded-xl border p-4 text-left ${d.id === selected?.id ? "border-primary bg-primary/5" : "border-border"}`}><div className="font-medium">{d.filename}</div><div className="text-xs text-muted-foreground">{d.rows.toLocaleString()} rows · {d.columns} columns</div></button>)}</div>
    {selected && <div className="grid gap-4 lg:grid-cols-3"><Card className="p-6 lg:col-span-2"><Input value={q} onChange={e => setQ(e.target.value)} placeholder="Search uploaded rows…"/><div className="mt-4 overflow-x-auto"><table className="w-full text-sm"><thead><tr>{Object.keys(preview.data?.rows?.[0] ?? {}).map(k => <th className="p-2 text-left" key={k}>{k}</th>)}</tr></thead><tbody>{(preview.data?.rows ?? []).map((row: Record<string, unknown>, i: number) => <tr key={i} className="border-t">{Object.entries(row).map(([k, v]) => <td className="p-2" key={k}>{String(v ?? "")}</td>)}</tr>)}</tbody></table></div><p className="mt-3 text-xs text-muted-foreground">Showing {preview.data?.rows?.length ?? 0} of {preview.data?.total ?? 0} matching uploaded rows.</p></Card>
      <Card className="p-6"><h3 className="font-semibold">Columns</h3><ul className="mt-3 space-y-2">{(columns.data ?? []).map((c: {name:string; type:string; missing:number; unique:number}) => <li key={c.name} className="rounded border p-2 text-sm"><div className="font-medium">{c.name}</div><div className="text-xs text-muted-foreground">{c.type} · {c.unique} unique · {c.missing} missing</div></li>)}</ul></Card></div>}
  </div>;
}
