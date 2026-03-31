import { useMutation } from '@tanstack/react-query'
import { AxiosError } from 'axios'
import { uploadDocument } from '../api/endpoints'
import { useToast } from '../components/ToastProvider'

export function useUploadDocument() {
  const { showToast } = useToast()

  return useMutation({
    mutationFn: (file: File) => uploadDocument(file),
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
