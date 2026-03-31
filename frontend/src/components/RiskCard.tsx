import type { Risk } from '../types'

interface RiskCardProps {
  risk: Risk
  onClick?: (risk: Risk) => void
}

const severityClass: Record<Risk['severity'], string> = {
  high: 'border-red-300 bg-red-50',
  medium: 'border-amber-300 bg-amber-50',
  low: 'border-emerald-300 bg-emerald-50',
}

export function RiskCard({ risk, onClick }: RiskCardProps) {
  return (
    <article
      className={`rounded-xl border p-4 shadow-sm transition ${severityClass[risk.severity]} ${
        onClick ? 'cursor-pointer hover:shadow-md' : ''
      }`}
      onClick={() => onClick?.(risk)}
    >
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-900">{risk.title}</h3>
        <span className="text-xs font-semibold uppercase text-slate-700">{risk.severity}</span>
      </div>
      <p className="mt-2 text-xs text-slate-700">Status: {risk.status}</p>
      <p className="text-xs text-slate-700">Source: {risk.source}</p>
    </article>
  )
}
