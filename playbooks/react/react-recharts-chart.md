# Recharts Line Chart Skill

## When to use
Building the 7-day Revenue Trend chart in React with Recharts.

## Pattern

```tsx
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from "recharts"

interface ChartPoint {
  label: string  // e.g. "2026-05-19"
  value: number  // revenue amount
}

interface RevenueTrendChartProps {
  data: ChartPoint[]
}

// Format date label to short form: "May 19"
function formatDate(label: string): string {
  try {
    const d = new Date(label)
    return d.toLocaleDateString("en-IE", { month: "short", day: "numeric" })
  } catch {
    return label
  }
}

// Format currency for tooltip
function formatCurrency(value: number): string {
  return `€${value.toLocaleString("en-IE", { minimumFractionDigits: 0 })}`
}

export function RevenueTrendChart({ data }: RevenueTrendChartProps) {
  const formatted = data.map(d => ({ ...d, label: formatDate(d.label) }))
  const total = data.reduce((sum, d) => sum + d.value, 0)
  const avg = data.length ? total / data.length : 0

  return (
    <div className="space-y-3">
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={formatted} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <defs>
            <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 11, fill: "#9ca3af" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: "#9ca3af" }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `€${v}`}
            width={50}
          />
          <Tooltip
            formatter={(value: number) => [formatCurrency(value), "Revenue"]}
            contentStyle={{
              background: "white",
              border: "1px solid #e5e7eb",
              borderRadius: "8px",
              fontSize: "12px",
            }}
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke="#3b82f6"
            strokeWidth={2}
            fill="url(#revenueGradient)"
            dot={{ r: 3, fill: "#3b82f6", strokeWidth: 0 }}
            activeDot={{ r: 5 }}
          />
        </AreaChart>
      </ResponsiveContainer>

      {/* Summary row below chart */}
      <div className="flex gap-6 px-2 pt-1 border-t border-gray-100">
        <div>
          <p className="text-xs text-gray-400">Total Revenue (7 days)</p>
          <p className="text-sm font-semibold text-gray-800">{formatCurrency(total)}</p>
        </div>
        <div>
          <p className="text-xs text-gray-400">Daily Average</p>
          <p className="text-sm font-semibold text-gray-800">{formatCurrency(avg)}</p>
        </div>
      </div>
    </div>
  )
}
```

## Rules
- Always use `ResponsiveContainer` — never fixed width
- Use `AreaChart` not `LineChart` — gradient fill matches target design
- Format dates: "May 19" not "2026-05-19" (use `formatDate` helper above)
- Format currency: `€1,250` not `1250` (Irish locale)
- Gradient fill: blue at top, transparent at bottom (`revenueGradient`)
- Summary row shows total + daily average below chart
- `vertical={false}` on CartesianGrid (horizontal lines only, cleaner)
