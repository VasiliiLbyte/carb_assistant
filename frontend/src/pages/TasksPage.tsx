import { useMemo, useState } from 'react'
import { Modal } from '../components/ui/Modal'
import { TaskList } from '../components/TaskList'
import { useTaskMutations, useTasks } from '../hooks/useTasks'
import type { Task } from '../types'

export function TasksPage() {
  const { data: tasks = [], isLoading } = useTasks()
  const { createTask, updateTask, deleteTask } = useTaskMutations()
  const [viewingTask, setViewingTask] = useState<Task | null>(null)
  const [editingTask, setEditingTask] = useState<Task | null>(null)
  const [isEditOpen, setIsEditOpen] = useState(false)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState<Task['priority']>('medium')
  const [status, setStatus] = useState<Task['status']>('to-do')

  if (isLoading) {
    return <p className="text-sm text-slate-500">Loading tasks...</p>
  }

  const modalFooter = useMemo(
    () => (
      <>
        <button
          type="button"
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
          onClick={() => setIsEditOpen(false)}
        >
          Отмена
        </button>
        <button
          type="button"
          className="rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-500"
          onClick={() => {
            if (!title.trim()) return
            const payload = { title: title.trim(), description, priority, status }
            if (editingTask) {
              updateTask.mutate({ id: editingTask.id, payload })
            } else {
              createTask.mutate(payload)
            }
            setIsEditOpen(false)
            setEditingTask(null)
            setTitle('')
            setDescription('')
          }}
        >
          Сохранить
        </button>
      </>
    ),
    [createTask, description, editingTask, priority, status, title, updateTask],
  )

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900">Задачи</h2>
        <button
          type="button"
          className="rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-500"
          onClick={() => {
            setViewingTask(null)
            setEditingTask(null)
            setTitle('')
            setDescription('')
            setPriority('medium')
            setStatus('to-do')
            setIsEditOpen(true)
          }}
        >
          Создать задачу
        </button>
      </div>

      <TaskList
        tasks={tasks}
          onTaskClick={(task) => setViewingTask(task)}
        actionSlot={(task) => (
          <div className="flex gap-2">
            <button
              type="button"
              className="rounded bg-slate-100 px-2 py-1 text-xs hover:bg-slate-200"
              onClick={() => {
                setEditingTask(task)
                setTitle(task.title)
                setDescription(task.description)
                setPriority(task.priority)
                setStatus(task.status)
                setIsEditOpen(true)
              }}
            >
              Редактировать
            </button>
            <button
              type="button"
              className="rounded bg-red-100 px-2 py-1 text-xs text-red-700 hover:bg-red-200"
              onClick={() => deleteTask.mutate(task.id)}
            >
              Удалить
            </button>
          </div>
        )}
      />

      <Modal
        isOpen={isEditOpen}
        onClose={() => {
          setIsEditOpen(false)
          setEditingTask(null)
        }}
        title={editingTask ? 'Редактирование задачи' : 'Создание задачи'}
        footer={modalFooter}
      >
        <input
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          placeholder="Название задачи"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
        />
        <textarea
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          placeholder="Описание"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
        />
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <select
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            value={priority}
            onChange={(event) => setPriority(event.target.value as Task['priority'])}
          >
            <option value="low">low</option>
            <option value="medium">medium</option>
            <option value="high">high</option>
            <option value="critical">critical</option>
          </select>
          <select
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            value={status}
            onChange={(event) => setStatus(event.target.value as Task['status'])}
          >
            <option value="to-do">to-do</option>
            <option value="in-progress">in-progress</option>
            <option value="blocked">blocked</option>
            <option value="done">done</option>
            <option value="canceled">canceled</option>
          </select>
        </div>
      </Modal>

      <Modal isOpen={Boolean(viewingTask)} onClose={() => setViewingTask(null)} title="Детали задачи">
        {viewingTask ? (
          <div className="space-y-2 text-sm">
            <p className="font-medium text-slate-800">{viewingTask.title}</p>
            <p className="text-slate-600">{viewingTask.description || 'Описание отсутствует'}</p>
            <p>
              Priority: <span className="font-medium">{viewingTask.priority}</span>
            </p>
            <p>
              Status: <span className="font-medium">{viewingTask.status}</span>
            </p>
          </div>
        ) : null}
      </Modal>
    </div>
  )
}
