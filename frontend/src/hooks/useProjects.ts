import { useQuery } from '@tanstack/react-query'
import { getProjects } from '../api/endpoints'

export const useProjects = () =>
  useQuery({
    queryKey: ['projects'],
    queryFn: getProjects,
    staleTime: 30_000,
    refetchInterval: 60_000,
  })
