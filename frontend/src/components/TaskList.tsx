import type { Task } from '../types'
import type { ReactNode } from 'react'

interface TaskListProps {
  tasks: Task[]
  onTaskClick?: (task: Task) => void
  actionSlot?: (task: Task) => ReactNode
}

const priorityClass: Record<Task['priority'], string> = {
  low: 'bg-green-100 text-green-700',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-red-100 text-red-700',
  critical: 'bg-red-200 text-red-800',
}

const statusClass: Record<Task['status'], string> = {
  'to-do': 'text-slate-600',
  'in-progress': 'text-indigo-700',
  blocked: 'text-red-700',
  done: 'text-green-700',
  canceled: 'text-slate-500',
}

export function TaskList({ tasks, onTaskClick, actionSlot }: TaskListProps) {
  return (
    <ul className="space-y-3">
      {tasks.map((task) => (
        <li
          key={task.id}
          className={`rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition ${
            onTaskClick ? 'cursor-pointer hover:border-indigo-300 hover:shadow-md' : ''
          }`}
          onClick={() => onTaskClick?.(task)}
        >
          <div className="flex items-center justify-between gap-3">
            <h3 className="text-sm font-semibold text-slate-900">{task.title}</h3>
            <span className={`rounded-full px-2 py-1 text-xs font-medium ${priorityClass[task.priority]}`}>
              {task.priority}
            </span>
          </div>
          <p className={`mt-2 text-xs font-medium ${statusClass[task.status]}`}>Status: {task.status}</p>
          {actionSlot ? <div className="mt-3" onClick={(event) => event.stopPropagation()}>{actionSlot(task)}</div> : null}
        </li>
      ))}
    </ul>
  )
}
