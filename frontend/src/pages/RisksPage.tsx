import { useState } from 'react'
import { RiskCard } from '../components/RiskCard'
import { Modal } from '../components/ui/Modal'
import { useRiskDetection, useRisks } from '../hooks/useRisks'
import { useTasks } from '../hooks/useTasks'
import type { Risk } from '../types'

export function RisksPage() {
  const { data: risks = [], isLoading } = useRisks()
  const { data: tasks = [] } = useTasks()
  const { detectFromTask, detectFromDocument, detectFromMessage } = useRiskDetection()
  const [selectedRisk, setSelectedRisk] = useState<Risk | null>(null)
  const [messageText, setMessageText] = useState('Potential delivery delay due to vendor dependency.')
  const [documentKey, setDocumentKey] = useState('')

  if (isLoading) {
    return <p className="text-sm text-slate-500">Loading risks...</p>
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          className="rounded-lg bg-amber-500 px-3 py-2 text-sm font-medium text-white hover:bg-amber-400"
          onClick={() => {
            if (tasks[0]) detectFromTask.mutate(tasks[0].id)
          }}
        >
          Detect risks from task
        </button>
        <button
          type="button"
          className="rounded-lg bg-amber-700 px-3 py-2 text-sm font-medium text-white hover:bg-amber-600"
          onClick={() => detectFromMessage.mutate({ message: messageText })}
        >
          Detect risks from message
        </button>
        <button
          type="button"
          className="rounded-lg bg-orange-700 px-3 py-2 text-sm font-medium text-white hover:bg-orange-600"
          onClick={() => {
            if (documentKey.trim()) {
              detectFromDocument.mutate({ documentKey: documentKey.trim() })
            }
          }}
        >
          Detect risks from document
        </button>
      </div>
      <input
        className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
        value={documentKey}
        placeholder="document_key (например: projects/<project_id>/documents/file.txt)"
        onChange={(event) => setDocumentKey(event.target.value)}
      />
      <textarea
        className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
        value={messageText}
        onChange={(event) => setMessageText(event.target.value)}
      />
      <div className="grid gap-3 md:grid-cols-2">
        {risks.map((risk) => (
          <RiskCard key={risk.id} risk={risk} onClick={setSelectedRisk} />
        ))}
      </div>
      <Modal isOpen={Boolean(selectedRisk)} onClose={() => setSelectedRisk(null)} title="Детали риска">
        {selectedRisk ? (
          <div className="space-y-2 text-sm">
            <p className="font-medium">{selectedRisk.title}</p>
            <p>Severity: {selectedRisk.severity}</p>
            <p>Status: {selectedRisk.status}</p>
            <p>Mitigation: {selectedRisk.mitigation_plan || 'N/A'}</p>
          </div>
        ) : null}
      </Modal>
    </div>
  )
}
