import { useMutation } from '@tanstack/react-query'
import { AxiosError } from 'axios'
import { uploadDocument } from '../api/endpoints'
import { useToast } from '../components/ToastProvider'

export function useUploadDocument() {
  const { showToast } = useToast()

  return useMutation({
    mutationFn: async () => {
      const file = new File(['Dashboard upload test'], 'dashboard-smoke.txt', { type: 'text/plain' })
      return uploadDocument(file)
    },
    onSuccess: (data) => {
      showToast(`Uploaded: ${data.filename}`, 'success')
    },
    onError: (error) => {
      const errorMessage =
        error instanceof AxiosError ? (error.response?.data?.detail as string | undefined) : undefined
      showToast(errorMessage ?? 'Document upload failed', 'error')
    },
  })
}
