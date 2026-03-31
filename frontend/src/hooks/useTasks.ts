import { useQuery } from '@tanstack/react-query'
import { getTasks } from '../api/endpoints'

export const useTasks = () =>
  useQuery({
    queryKey: ['tasks'],
    queryFn: getTasks,
    staleTime: 20_000,
    refetchInterval: 45_000,
  })
