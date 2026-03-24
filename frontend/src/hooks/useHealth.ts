import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api/client'

export function useHealth() {
  return useQuery({ queryKey: ['health'], queryFn: async () => (await apiClient.get('/health')).data })
}
