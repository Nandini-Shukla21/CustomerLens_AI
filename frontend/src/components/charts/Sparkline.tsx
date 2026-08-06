import { Area, AreaChart, ResponsiveContainer } from "recharts";

export function Sparkline({ data, trend = "up" }: { data: number[]; trend?: "up" | "down" }) {
  const rows = data.map((v, i) => ({ i, v }));
  const color = trend === "down" ? "var(--destructive)" : "var(--brand)";
  const id = `spark-${Math.random().toString(36).slice(2, 8)}`;
  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={rows} margin={{ top: 0, right: 0, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.35} />
            <stop offset="100%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <Area type="monotone" dataKey="v" stroke={color} strokeWidth={2} fill={`url(#${id})`} />
      </AreaChart>
    </ResponsiveContainer>
  );
}
