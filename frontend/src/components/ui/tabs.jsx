import * as React from "react"

export function Tabs({ children }) {
  return <div>{children}</div>
}
export function TabsList({ children, className }) {
  return <div className={`flex border-b mb-4 ${className}`}>{children}</div>
}
export function TabsTrigger({ children }) {
  return (
    <button className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 border-b-2 border-transparent hover:border-primary">
      {children}
    </button>
  )
}
export function TabsContent({ children }) {
  return <div className="mt-4">{children}</div>
}

