import { useMutation, useQueryClient } from '@tanstack/react-query'
import { AxiosError } from 'axios'
import { createTask } from '../api/endpoints'
import { useToast } from '../components/ToastProvider'

export function useCreateTask() {
  const queryClient = useQueryClient()
  const { showToast } = useToast()

  return useMutation({
    mutationFn: () =>
      createTask({
        title: `Quick task ${new Date().toLocaleTimeString()}`,
        description: 'Created from dashboard',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      showToast('Task created successfully', 'success')
    },
    onError: (error) => {
      const errorMessage =
        error instanceof AxiosError ? (error.response?.data?.detail as string | undefined) : undefined
      showToast(errorMessage ?? 'Failed to create task', 'error')
    },
  })
}
