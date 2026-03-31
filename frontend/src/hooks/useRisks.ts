import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { detectRisksFromDocument, detectRisksFromMessage, detectRisksFromTask, getRisks } from '../api/endpoints'
import { useToast } from '../components/ToastProvider'

export const useRisks = () =>
  useQuery({
    queryKey: ['risks'],
    queryFn: getRisks,
    staleTime: 15_000,
    refetchInterval: 30_000,
  })

export function useRiskDetection() {
  const queryClient = useQueryClient()
  const { showToast } = useToast()

  const onSuccess = (createdCount: number) => {
    queryClient.invalidateQueries({ queryKey: ['risks'] })
    showToast(`Обнаружено рисков: ${createdCount}`, 'success')
  }

  return {
    detectFromTask: useMutation({
      mutationFn: (taskId: string) => detectRisksFromTask(taskId),
      onSuccess: (data) => onSuccess(data.created_count),
      onError: () => showToast('Не удалось выполнить risk detection по задаче', 'error'),
    }),
    detectFromDocument: useMutation({
      mutationFn: ({ documentKey, projectId }: { documentKey: string; projectId?: string }) =>
        detectRisksFromDocument(documentKey, projectId),
      onSuccess: (data) => onSuccess(data.created_count),
      onError: () => showToast('Не удалось выполнить risk detection по документу', 'error'),
    }),
    detectFromMessage: useMutation({
      mutationFn: ({ message, projectId }: { message: string; projectId?: string }) =>
        detectRisksFromMessage(message, projectId),
      onSuccess: (data) => onSuccess(data.created_count),
      onError: () => showToast('Не удалось выполнить risk detection по сообщению', 'error'),
    }),
  }
}
