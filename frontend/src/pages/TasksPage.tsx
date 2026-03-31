import { TaskList } from '../components/TaskList'
import { useTasks } from '../hooks/useTasks'

export function TasksPage() {
  const { data: tasks = [], isLoading } = useTasks()

  if (isLoading) {
    return <p className="text-sm text-slate-500">Loading tasks...</p>
  }

  return <TaskList tasks={tasks} />
}
