import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { PageHeader } from "@/components/ui/PageHeader";
import { platformApi } from "@/api/platform";

export const Route = createFileRoute("/_app/customer-360")({ component: Customer360 });
type Customer = { id:string; name:string; email?:string; phone?:string; revenue:number; transactions:number; ltv:number; risk:number; churn:number; payload: Record<string, unknown> };
function Customer360() {
  const [q, setQ] = useState(""); const { data: customers = [] } = useQuery<Customer[]>({ queryKey: ["customers", q], queryFn: () => platformApi.customers(q) });
  const [id, setId] = useState<string>(); useEffect(() => { if (!id && customers[0]) setId(customers[0].id); }, [customers, id]);
  const detail = useQuery({ queryKey: ["customer", id], queryFn: () => platformApi.customer(id!), enabled: !!id }); const c: Customer | undefined = detail.data?.profile;
  const value = (keys: string[]) => keys.map(k => c?.payload?.[k]).find(v => v != null);
  return <div className="space-y-6"><PageHeader eyebrow="Customer 360" title={c?.name ?? "Uploaded customers"} description={c ? `Customer ID: ${c.id}` : "Choose a customer from your uploaded dataset."}/>
    <Input value={q} onChange={e => setQ(e.target.value)} placeholder="Search uploaded customers by name, ID, email, or phone…"/>
    <div className="grid gap-3 md:grid-cols-3">{customers.map(customer => <button key={customer.id} onClick={() => setId(customer.id)} className={`rounded-xl border p-4 text-left ${customer.id === id ? "border-primary bg-primary/5" : "border-border"}`}><div className="font-medium">{customer.name}</div><div className="text-xs text-muted-foreground">{customer.email ?? customer.id}</div></button>)}</div>
    {c && <div className="grid gap-4 lg:grid-cols-[320px_1fr]"><Card className="p-6"><h2 className="text-xl font-semibold">{c.name}</h2><p className="text-sm text-muted-foreground">{c.email ?? "No email supplied"}</p><dl className="mt-5 space-y-3 text-sm">{Object.entries(c.payload).slice(0, 12).map(([key, value]) => <div key={key} className="flex justify-between gap-3"><dt className="text-muted-foreground">{key}</dt><dd className="text-right font-medium">{String(value ?? "")}</dd></div>)}</dl></Card>
      <div className="space-y-4"><div className="grid gap-4 md:grid-cols-3">{[["Revenue", c.revenue], ["Transactions", c.transactions], ["Lifetime value", c.ltv]].map(([label, value]) => <Card className="p-5" key={String(label)}><div className="text-xs text-muted-foreground">{label}</div><div className="mt-1 text-xl font-bold">{label === "Transactions" ? Number(value).toLocaleString() : `$${Number(value).toLocaleString()}`}</div></Card>)}</div>
      <Card className="p-6"><h3 className="font-semibold">Risk signals from uploaded data</h3><div className="mt-4 space-y-4"><Risk label="Risk score" value={c.risk}/><Risk label="Churn score" value={c.churn}/></div><p className="mt-5 text-sm text-muted-foreground">{detail.data?.ai_summary}</p></Card>
      <Card className="p-6"><h3 className="font-semibold">Customer data</h3><div className="mt-3 flex flex-wrap gap-2">{Object.entries(c.payload).map(([key, v]) => <Badge key={key} variant="outline">{key}: {String(v ?? "")}</Badge>)}</div></Card></div></div>}
  </div>;
}
function Risk({ label, value }: {label:string; value:number}) { return <div><div className="flex justify-between text-sm"><span>{label}</span><span>{(value * 100).toFixed(0)}%</span></div><Progress className="mt-1" value={value * 100}/></div>; }
