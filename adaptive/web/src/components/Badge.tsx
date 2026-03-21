type Variant = 'blue' | 'green' | 'red' | 'yellow' | 'gray'

const cls: Record<Variant, string> = {
  blue:   'text-brand-400 bg-brand-500/10 border-brand-500/20',
  green:  'text-success-400 bg-success-500/10 border-success-500/20',
  red:    'text-danger-400 bg-danger-500/10 border-danger-500/20',
  yellow: 'text-warning-400 bg-warning-500/10 border-warning-500/20',
  gray:   'text-slate-500 bg-dark-600/60 border-dark-500/60',
}

export function Badge({ label, variant = 'gray' }: { label: string; variant?: Variant }) {
  return (
    <span
      className={`inline-flex items-center text-xs font-medium px-1.5 py-0.5
        rounded border tracking-wide font-mono ${cls[variant]}`}
      style={{ fontFamily: "'Fira Code', monospace", fontSize: 11 }}
    >
      {label}
    </span>
  )
}
