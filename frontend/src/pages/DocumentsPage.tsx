import { useState } from 'react'
import { Modal } from '../components/ui/Modal'
import { useUploadDocument } from '../hooks/useUploadDocument'

export function DocumentsPage() {
  const [message, setMessage] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const uploadMutation = useUploadDocument()

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-slate-900">Documents</h2>
        <button
          type="button"
          className="rounded-lg bg-slate-900 px-3 py-2 text-sm font-medium text-white hover:bg-slate-700"
          onClick={() => setIsModalOpen(true)}
        >
          Загрузить документ
        </button>
      </div>
      {message && <p className="mt-3 text-sm text-emerald-700">{message}</p>}

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Загрузка документа">
        <input
          type="file"
          className="block w-full rounded-lg border border-slate-300 p-2 text-sm"
          onChange={(event) => {
            const file = event.target.files?.[0]
            if (!file) return
            uploadMutation.mutate(file, {
              onSuccess: (data) => {
                setMessage(`Uploaded: ${data.filename}`)
                setIsModalOpen(false)
              },
            })
          }}
        />
      </Modal>
    </div>
  )
}
