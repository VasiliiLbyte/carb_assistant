import { RiskCard } from '../components/RiskCard'
import { useRisks } from '../hooks/useRisks'

export function RisksPage() {
  const { data: risks = [], isLoading } = useRisks()

  if (isLoading) {
    return <p className="text-sm text-slate-500">Loading risks...</p>
  }

  return (
    <div className="grid gap-3 md:grid-cols-2">
      {risks.map((risk) => (
        <RiskCard key={risk.id} risk={risk} />
      ))}
    </div>
  )
}
