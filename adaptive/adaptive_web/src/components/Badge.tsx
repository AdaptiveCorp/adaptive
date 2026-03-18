type Variant = 'blue' | 'green' | 'red' | 'yellow' | 'gray'

const styles: Record<Variant, string> = {
  blue: 'bg-brand-600/20 text-brand-400 border-brand-600/30',
  green: 'bg-success-500/20 text-success-400 border-success-500/30',
  red: 'bg-danger-500/20 text-danger-400 border-danger-500/30',
  yellow: 'bg-warning-500/20 text-warning-400 border-warning-500/30',
  gray: 'bg-slate-600/20 text-slate-400 border-slate-600/30',
}

interface BadgeProps {
  label: string
  variant?: Variant
}

export function Badge({ label, variant = 'gray' }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center text-xs font-medium px-2 py-0.5 rounded-full border ${styles[variant]}`}
    >
      {label}
    </span>
  )
}
