import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createProject, deleteProject, getProjects, updateProject } from '../api/endpoints'
import { useToast } from '../components/ToastProvider'
import type { ProjectPayload } from '../types'

export const useProjects = () =>
  useQuery({
    queryKey: ['projects'],
    queryFn: getProjects,
    staleTime: 30_000,
    refetchInterval: 60_000,
  })

export function useProjectMutations() {
  const queryClient = useQueryClient()
  const { showToast } = useToast()

  const onSuccess = (message: string) => {
    queryClient.invalidateQueries({ queryKey: ['projects'] })
    showToast(message, 'success')
  }

  return {
    createProject: useMutation({
      mutationFn: (payload: ProjectPayload) => createProject(payload),
      onSuccess: () => onSuccess('Проект создан'),
      onError: () => showToast('Не удалось создать проект', 'error'),
    }),
    updateProject: useMutation({
      mutationFn: ({ id, payload }: { id: string; payload: Partial<ProjectPayload> }) => updateProject(id, payload),
      onSuccess: () => onSuccess('Проект обновлен'),
      onError: () => showToast('Не удалось обновить проект', 'error'),
    }),
    deleteProject: useMutation({
      mutationFn: (id: string) => deleteProject(id),
      onSuccess: () => onSuccess('Проект удален'),
      onError: () => showToast('Не удалось удалить проект', 'error'),
    }),
  }
}
