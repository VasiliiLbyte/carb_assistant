import { useQuery } from '@tanstack/react-query'
import { getRisks } from '../api/endpoints'

export const useRisks = () =>
  useQuery({
    queryKey: ['risks'],
    queryFn: getRisks,
    staleTime: 15_000,
    refetchInterval: 30_000,
  })
