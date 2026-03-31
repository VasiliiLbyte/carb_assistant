import { useMutation } from '@tanstack/react-query'
import { triggerProactive } from '../api/endpoints'
import { useToast } from '../components/ToastProvider'
import { AxiosError } from 'axios'

export function useTriggerProactive(taskId: string | undefined, ruleId: string | undefined) {
  const { showToast } = useToast()

  return useMutation({
    mutationFn: async () => {
      if (!taskId || !ruleId) {
        throw new Error('Task and rule are required for proactive trigger')
      }
      return triggerProactive(ruleId, taskId)
    },
    onSuccess: () => {
      showToast('Proactive trigger sent', 'success')
    },
    onError: (error) => {
      const errorMessage =
        error instanceof AxiosError ? (error.response?.data?.detail as string | undefined) : undefined
      showToast(errorMessage ?? 'Failed to send proactive trigger', 'error')
    },
  })
}
