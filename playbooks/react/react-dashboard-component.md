# React Dashboard Component Skill

## When to use
Building a dashboard card/panel widget in React + TypeScript with shadcn/ui and Tailwind CSS.

## Core Pattern

```tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

interface MyPanelProps {
  title: string
  onViewAll?: () => void
  isLoading?: boolean
  error?: string | null
}

export function MyPanel({ title, onViewAll, isLoading, error }: MyPanelProps) {
  if (isLoading) return (
    <Card><CardContent className="p-6"><div className="animate-pulse h-32 bg-gray-100 rounded" /></CardContent></Card>
  )

  if (error) return (
    <Card><CardContent className="p-6 text-red-500 text-sm">{error}</CardContent></Card>
  )

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-semibold text-gray-700">{title}</CardTitle>
        {onViewAll && (
          <Button variant="ghost" size="sm" onClick={onViewAll} className="text-blue-600 text-xs">
            View All
          </Button>
        )}
      </CardHeader>
      <CardContent>
        {/* content here */}
      </CardContent>
    </Card>
  )
}
```

## KPI Card Pattern

```tsx
import { TrendingUp, TrendingDown } from "lucide-react"

interface KpiCardProps {
  title: string
  value: string | number
  change?: number
  changePeriod?: string
  icon: React.ReactNode
  color: "blue" | "orange" | "green" | "red"
  onClick?: () => void
}

const colorMap = {
  blue:   { bg: "bg-blue-50",   icon: "text-blue-600",   gradient: "from-blue-500 to-blue-600" },
  orange: { bg: "bg-orange-50", icon: "text-orange-600", gradient: "from-orange-500 to-orange-600" },
  green:  { bg: "bg-green-50",  icon: "text-green-600",  gradient: "from-green-500 to-green-600" },
  red:    { bg: "bg-red-50",    icon: "text-red-600",    gradient: "from-red-500 to-red-600" },
}

export function KpiCard({ title, value, change, changePeriod, icon, color, onClick }: KpiCardProps) {
  const c = colorMap[color]
  return (
    <Card
      className={`cursor-pointer hover:shadow-md transition-shadow ${onClick ? "cursor-pointer" : ""}`}
      onClick={onClick}
    >
      <CardContent className="p-4">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${c.bg}`}>
            <span className={c.icon}>{icon}</span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs text-gray-500 truncate">{title}</p>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
            {change !== undefined && (
              <p className={`text-xs flex items-center gap-1 ${change >= 0 ? "text-green-600" : "text-red-500"}`}>
                {change >= 0 ? <TrendingUp size={10} /> : <TrendingDown size={10} />}
                {Math.abs(change)}% {changePeriod}
              </p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
```

## Rules
- Always handle loading and error states
- Use `text-sm` for labels, `text-2xl font-bold` for values
- Cards use `hover:shadow-md transition-shadow` when clickable
- Import from `@/components/ui/...` (shadcn path alias)
- Tailwind only — no inline styles
