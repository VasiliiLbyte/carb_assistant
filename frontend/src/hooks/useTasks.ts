import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createTask, deleteTask, getTasks, updateTask } from '../api/endpoints'
import { useToast } from '../components/ToastProvider'
import type { TaskPayload } from '../types'

export const useTasks = () =>
  useQuery({
    queryKey: ['tasks'],
    queryFn: getTasks,
    staleTime: 20_000,
    refetchInterval: 45_000,
  })

export function useTaskMutations() {
  const queryClient = useQueryClient()
  const { showToast } = useToast()

  const onSuccess = (message: string) => {
    queryClient.invalidateQueries({ queryKey: ['tasks'] })
    queryClient.invalidateQueries({ queryKey: ['risks'] })
    showToast(message, 'success')
  }

  return {
    createTask: useMutation({
      mutationFn: (payload: TaskPayload) => createTask(payload),
      onSuccess: () => onSuccess('Задача создана'),
      onError: () => showToast('Не удалось создать задачу', 'error'),
    }),
    updateTask: useMutation({
      mutationFn: ({ id, payload }: { id: string; payload: Partial<TaskPayload> }) => updateTask(id, payload),
      onSuccess: () => onSuccess('Задача обновлена'),
      onError: () => showToast('Не удалось обновить задачу', 'error'),
    }),
    deleteTask: useMutation({
      mutationFn: (id: string) => deleteTask(id),
      onSuccess: () => onSuccess('Задача удалена'),
      onError: () => showToast('Не удалось удалить задачу', 'error'),
    }),
  }
}
