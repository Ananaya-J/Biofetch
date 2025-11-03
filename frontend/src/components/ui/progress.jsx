import * as React from "react"

export function Progress({ value }) {
  return (
    <div className="w-full bg-secondary h-2 rounded">
      <div
        className="bg-primary h-2 rounded transition-all"
        style={{ width: `${value}%` }}
      ></div>
    </div>
  )
}

