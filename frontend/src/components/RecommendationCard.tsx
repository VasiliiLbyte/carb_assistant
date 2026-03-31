import type { Recommendation } from '../types'

interface RecommendationCardProps {
  recommendation: Recommendation | undefined
  isLoading: boolean
}

export function RecommendationCard({ recommendation, isLoading }: RecommendationCardProps) {
  if (isLoading) {
    return <div className="rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-500">Loading...</div>
  }

  if (!recommendation) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-500">
        No recommendation available
      </div>
    )
  }

  return (
    <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h3 className="text-sm font-semibold text-slate-900">{recommendation.recommended_user_name ?? 'No assignee'}</h3>
      <p className="mt-2 text-xs text-slate-600">{recommendation.reason}</p>
    </article>
  )
}
