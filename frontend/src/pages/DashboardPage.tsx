import { useEffect, useState } from 'react'
import { ProjectCard } from '../components/ProjectCard'
import { RecommendationCard } from '../components/RecommendationCard'
import { RiskCard } from '../components/RiskCard'
import { TaskList } from '../components/TaskList'
import { useCreateTask } from '../hooks/useCreateTask'
import { useProactiveRules } from '../hooks/useProactiveRules'
import { useProjects } from '../hooks/useProjects'
import { useRecommender } from '../hooks/useRecommender'
import { useRisks } from '../hooks/useRisks'
import { useTasks } from '../hooks/useTasks'
import { useTriggerProactive } from '../hooks/useTriggerProactive'
import { useUploadDocument } from '../hooks/useUploadDocument'

export function DashboardPage() {
  const { data: projects = [] } = useProjects()
  const { data: tasks = [] } = useTasks()
  const { data: risks = [] } = useRisks()
  const { data: proactiveRules = [] } = useProactiveRules()
  const [selectedTaskId, setSelectedTaskId] = useState<string | undefined>(undefined)
  const [selectedRuleId, setSelectedRuleId] = useState<string | undefined>(undefined)
  const { data: recommendation, isLoading: recommendationLoading } = useRecommender(selectedTaskId)
  const createTaskMutation = useCreateTask()
  const proactiveMutation = useTriggerProactive(selectedTaskId, selectedRuleId)
  const uploadMutation = useUploadDocument()

  useEffect(() => {
    if (!selectedTaskId && tasks.length > 0) {
      setSelectedTaskId(tasks[0].id)
    }
  }, [selectedTaskId, tasks])

  useEffect(() => {
    if (!selectedRuleId && proactiveRules.length > 0) {
      setSelectedRuleId(proactiveRules[0].id)
    }
  }, [proactiveRules, selectedRuleId])

  return (
    <main className="space-y-6">
      <header className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          className="rounded-lg bg-slate-900 px-3 py-2 text-sm font-medium text-white hover:bg-slate-700"
          onClick={() => uploadMutation.mutate()}
        >
          Загрузить документ
        </button>
        <button
          type="button"
          className="rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-500"
          onClick={() => createTaskMutation.mutate()}
        >
          Создать задачу
        </button>
        <button
          type="button"
          className="rounded-lg bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-500"
          onClick={() => proactiveMutation.mutate()}
          disabled={!selectedTaskId || !selectedRuleId}
        >
          Триггер proactive
        </button>
      </header>

      <section className="grid gap-3 md:grid-cols-2">
        <label className="text-sm">
          <span className="mb-1 block text-slate-700">Active task</span>
          <select
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2"
            value={selectedTaskId ?? ''}
            onChange={(event) => setSelectedTaskId(event.target.value || undefined)}
          >
            {tasks.length === 0 && <option value="">No tasks available</option>}
            {tasks.map((task) => (
              <option key={task.id} value={task.id}>
                {task.title}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          <span className="mb-1 block text-slate-700">Proactive rule</span>
          <select
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2"
            value={selectedRuleId ?? ''}
            onChange={(event) => setSelectedRuleId(event.target.value || undefined)}
          >
            {proactiveRules.length === 0 && <option value="">No rules available</option>}
            {proactiveRules.map((rule) => (
              <option key={rule.id} value={rule.id}>
                {rule.name}
              </option>
            ))}
          </select>
        </label>
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold text-slate-900">Projects</h2>
        <div className="grid gap-3 md:grid-cols-2">
          {projects.slice(0, 4).map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold text-slate-900">Tasks</h2>
        <TaskList tasks={tasks.slice(0, 6)} />
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold text-slate-900">Risks</h2>
        <div className="grid gap-3 md:grid-cols-2">
          {risks.slice(0, 4).map((risk) => (
            <RiskCard key={risk.id} risk={risk} />
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold text-slate-900">Recommendation</h2>
        <RecommendationCard recommendation={recommendation} isLoading={recommendationLoading} />
      </section>
    </main>
  )
}
