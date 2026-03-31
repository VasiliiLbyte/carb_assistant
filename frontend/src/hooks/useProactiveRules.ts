import { useQuery } from '@tanstack/react-query'
import { getProactiveRules } from '../api/endpoints'

export const useProactiveRules = () =>
  useQuery({
    queryKey: ['proactive-rules'],
    queryFn: getProactiveRules,
    staleTime: 60_000,
    refetchInterval: 90_000,
  })
