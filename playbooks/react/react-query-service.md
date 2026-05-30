# React Query + Axios Service Skill

## When to use
Fetching data from the GarageHQ Flask backend (localhost:5000) in React components.

## Auth Token
Token is stored in localStorage as `auth_token`. Always include as Bearer header.

## API Service Pattern

```typescript
// src/services/api.ts
import axios from "axios"

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:5000/api"

export const api = axios.create({ baseURL: API_BASE })

// Inject auth token on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("auth_token")
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Redirect to login on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("auth_token")
      window.location.href = "/login"
    }
    return Promise.reject(err)
  }
)
```

## Dashboard Service Pattern

```typescript
// src/services/dashboardService.ts
import { api } from "./api"

export interface DashboardAlert {
  id: string
  type: string
  message: string
  severity: "critical" | "warning"
  related_entity_id?: string
  timestamp: string
}

export interface JobSnapshot {
  work_order_id: string
  status: string
  vehicle: { make: string; model: string; license_plate: string } | null
  technician: { name: string } | null
  issue_type: string
  delivery_status: "on_track" | "at_risk" | "delayed"
  days_elapsed: number
}

export interface SupplyIssue {
  po_number: string
  supplier_name: string
  status: string
  days_overdue: number
  affected_jobs_count: number
}

export interface DashboardOverview {
  alerts: DashboardAlert[]
  jobs: JobSnapshot[]
  supply_issues: SupplyIssue[]
  revenue_trend: Array<{ label: string; value: number }>
  generated_at: string
}

export interface KpiCard {
  title: string
  value: string | number
  change?: number
  change_period?: string
  color?: string
  icon?: string
}

export const dashboardService = {
  getOverview: async (): Promise<DashboardOverview> => {
    const { data } = await api.get("/dashboard/overview")
    return data.data
  },
  getKpis: async (preset = "today"): Promise<KpiCard[]> => {
    const { data } = await api.get(`/dashboard/kpis?type=executive&preset=${preset}`)
    return data.data?.kpis ?? []
  },
  getAlerts: async (): Promise<DashboardAlert[]> => {
    const { data } = await api.get("/dashboard/alerts")
    return data.data?.alerts ?? []
  },
  getJobsSnapshot: async (): Promise<JobSnapshot[]> => {
    const { data } = await api.get("/dashboard/jobs-snapshot")
    const d = data.data
    return Array.isArray(d) ? d : d?.jobs ?? []
  },
  getSupplyIssues: async (): Promise<SupplyIssue[]> => {
    const { data } = await api.get("/dashboard/supply-issues")
    return data.data?.supply_issues ?? []
  },
}
```

## React Query Hook Pattern

```typescript
// src/hooks/useDashboard.ts
import { useQuery } from "@tanstack/react-query"
import { dashboardService } from "../services/dashboardService"

export function useDashboardOverview() {
  return useQuery({
    queryKey: ["dashboard", "overview"],
    queryFn: dashboardService.getOverview,
    refetchInterval: 60_000,  // auto-refresh every 60s
    staleTime: 30_000,
  })
}

export function useDashboardKpis() {
  return useQuery({
    queryKey: ["dashboard", "kpis"],
    queryFn: () => dashboardService.getKpis("today"),
    refetchInterval: 60_000,
  })
}
```

## Usage in Component

```tsx
function AlertsPanel() {
  const { data: overview, isLoading, error } = useDashboardOverview()

  if (isLoading) return <div className="animate-pulse h-48 bg-gray-100 rounded-lg" />
  if (error) return <div className="text-red-500 text-sm p-4">Failed to load alerts</div>

  return (
    <div>
      {overview?.alerts.map(alert => (
        <div key={alert.id}>{alert.message}</div>
      ))}
    </div>
  )
}
```

## Rules
- Always use `useQuery` from `@tanstack/react-query` — never raw `useEffect` + `useState` for data fetching
- `refetchInterval: 60_000` on all dashboard queries (60-second auto-refresh)
- Always handle `isLoading` and `error` states
- API base from `import.meta.env.VITE_API_BASE` with fallback to `http://localhost:5000/api`
