import * as React from "react"

export function Select({ children, value, onValueChange }) {
  return <div>{children}</div>
}
export function SelectTrigger({ children }) {
  return <div className="border rounded-md p-2 bg-white">{children}</div>
}
export function SelectValue({ placeholder }) {
  return <span className="text-gray-500">{placeholder}</span>
}
export function SelectContent({ children }) {
  return <div className="border rounded-md mt-1 bg-white">{children}</div>
}
export function SelectItem({ children, value }) {
  return <div className="p-2 hover:bg-gray-100 cursor-pointer">{children}</div>
}

