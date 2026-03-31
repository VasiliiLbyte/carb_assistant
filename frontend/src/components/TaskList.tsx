import type { Task } from '../types'

interface TaskListProps {
  tasks: Task[]
}

const priorityClass: Record<Task['priority'], string> = {
  low: 'bg-green-100 text-green-700',
  medium: 'bg-blue-100 text-blue-700',
  high: 'bg-orange-100 text-orange-700',
  critical: 'bg-red-100 text-red-700',
}

export function TaskList({ tasks }: TaskListProps) {
  return (
    <ul className="space-y-3">
      {tasks.map((task) => (
        <li key={task.id} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="flex items-center justify-between gap-3">
            <h3 className="text-sm font-semibold text-slate-900">{task.title}</h3>
            <span className={`rounded-full px-2 py-1 text-xs font-medium ${priorityClass[task.priority]}`}>
              {task.priority}
            </span>
          </div>
          <p className="mt-2 text-xs text-slate-500">Status: {task.status}</p>
        </li>
      ))}
    </ul>
  )
}
