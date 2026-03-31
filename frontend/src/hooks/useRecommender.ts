import { useMutation } from '@tanstack/react-query'
import { getRecommendation } from '../api/endpoints'
import { useToast } from '../components/ToastProvider'

export function useRecommender() {
  const { showToast } = useToast()

  return useMutation({
    mutationFn: (taskId: string) => getRecommendation(taskId),
    onError: () => showToast('Не удалось получить рекомендацию', 'error'),
  })
}
