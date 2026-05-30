# TanStack Table (React Table) Skill

## When to use
Building data tables with sorting, filtering, status badges in React + TypeScript.

## Installation
```bash
npm install @tanstack/react-table
```

## Status Badge Pattern

```tsx
// src/components/StatusBadge.tsx
const statusConfig = {
  in_progress:   { label: "In Progress",    className: "bg-blue-100 text-blue-700" },
  new:           { label: "New",            className: "bg-gray-100 text-gray-700" },
  waiting_parts: { label: "Waiting Parts",  className: "bg-yellow-100 text-yellow-700" },
  completed:     { label: "Completed",      className: "bg-green-100 text-green-700" },
  cancelled:     { label: "Cancelled",      className: "bg-red-100 text-red-700" },
  delayed:       { label: "Delayed",        className: "bg-red-100 text-red-700" },
  at_risk:       { label: "At Risk",        className: "bg-yellow-100 text-yellow-700" },
  on_track:      { label: "On Track",       className: "bg-green-100 text-green-700" },
} as const

export function StatusBadge({ status }: { status: string }) {
  const config = statusConfig[status as keyof typeof statusConfig]
    ?? { label: status, className: "bg-gray-100 text-gray-600" }
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${config.className}`}>
      {config.label}
    </span>
  )
}
```

## Full Table Pattern

```tsx
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
  SortingState,
} from "@tanstack/react-table"
import { useState } from "react"
import { ChevronUp, ChevronDown } from "lucide-react"
import { StatusBadge } from "./StatusBadge"

interface JobSnapshot {
  work_order_id: string
  vehicle: { make: string; model: string; license_plate: string } | null
  issue_type: string
  status: string
  technician: { name: string } | null
  delivery_status: string
  days_elapsed: number
}

const columnHelper = createColumnHelper<JobSnapshot>()

const columns = [
  columnHelper.accessor(row => row.vehicle, {
    id: "vehicle",
    header: "Vehicle",
    cell: info => {
      const v = info.getValue()
      return v ? `${v.make} ${v.model} (${v.license_plate})` : "—"
    },
  }),
  columnHelper.accessor("work_order_id", {
    header: "Job ID",
    cell: info => (
      <span className="font-mono text-xs text-gray-600">{info.getValue().slice(0,12)}</span>
    ),
  }),
  columnHelper.accessor("issue_type", { header: "Issue Type" }),
  columnHelper.accessor("status", {
    header: "Status",
    cell: info => <StatusBadge status={info.getValue()} />,
  }),
  columnHelper.accessor(row => row.technician?.name ?? "—", {
    id: "technician",
    header: "Technician",
  }),
  columnHelper.accessor("delivery_status", {
    header: "Delivery",
    cell: info => <StatusBadge status={info.getValue()} />,
  }),
  columnHelper.accessor("days_elapsed", {
    header: "Days",
    cell: info => <span className={info.getValue() > 7 ? "text-red-600 font-medium" : ""}>{info.getValue()}</span>,
  }),
]

export function JobsSnapshotTable({ data }: { data: JobSnapshot[] }) {
  const [sorting, setSorting] = useState<SortingState>([])

  const table = useReactTable({
    data,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  })

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          {table.getHeaderGroups().map(hg => (
            <tr key={hg.id} className="border-b border-gray-100">
              {hg.headers.map(header => (
                <th
                  key={header.id}
                  className="px-3 py-2 text-left text-xs font-semibold text-gray-500 cursor-pointer select-none whitespace-nowrap"
                  onClick={header.column.getToggleSortingHandler()}
                >
                  <div className="flex items-center gap-1">
                    {flexRender(header.column.columnDef.header, header.getContext())}
                    {header.column.getIsSorted() === "asc" && <ChevronUp size={12} />}
                    {header.column.getIsSorted() === "desc" && <ChevronDown size={12} />}
                  </div>
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.length === 0 ? (
            <tr><td colSpan={columns.length} className="px-3 py-8 text-center text-gray-400 text-sm">No active jobs</td></tr>
          ) : (
            table.getRowModel().rows.map(row => (
              <tr key={row.id} className="border-b border-gray-50 hover:bg-gray-50 cursor-pointer">
                {row.getVisibleCells().map(cell => (
                  <td key={cell.id} className="px-3 py-2 whitespace-nowrap">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}
```

## Rules
- Sort by `days_elapsed` descending by default (most delayed first)
- Empty state: "No active jobs" centered text
- `overflow-x-auto` on container for mobile scroll
- Sticky header: add `sticky top-0 bg-white z-10` to `<thead>`
- Row click: pass `onRowClick?: (row: T) => void` prop
