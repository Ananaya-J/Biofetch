export function Alert({ children, variant = "default" }) {
  const base = "rounded-md p-4 border text-sm"
  const variants = {
    default: "bg-muted text-foreground",
    destructive: "border-red-400 bg-red-50 text-red-700"
  }
  return <div className={`${base} ${variants[variant]}`}>{children}</div>
}

export function AlertDescription({ children }) {
  return <div className="text-sm mt-1">{children}</div>
}

