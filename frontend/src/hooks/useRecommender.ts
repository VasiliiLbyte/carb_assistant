import { useQuery } from '@tanstack/react-query'
import { getRecommendation } from '../api/endpoints'

export const useRecommender = (taskId?: string) =>
  useQuery({
    queryKey: ['recommender', taskId],
    queryFn: () => getRecommendation(taskId!),
    enabled: Boolean(taskId),
    staleTime: 60_000,
  })
