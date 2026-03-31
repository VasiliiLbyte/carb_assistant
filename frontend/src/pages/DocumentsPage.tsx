import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { uploadDocument } from '../api/endpoints'

export function DocumentsPage() {
  const [message, setMessage] = useState('')
  const uploadMutation = useMutation({
    mutationFn: (file: File) => uploadDocument(file),
    onSuccess: (data) => setMessage(`Uploaded: ${data.filename}`),
  })

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <h2 className="text-lg font-semibold text-slate-900">Upload document</h2>
      <input
        type="file"
        className="mt-3 block text-sm"
        onChange={(event) => {
          const file = event.target.files?.[0]
          if (file) uploadMutation.mutate(file)
        }}
      />
      {message && <p className="mt-3 text-sm text-emerald-700">{message}</p>}
    </div>
  )
}
