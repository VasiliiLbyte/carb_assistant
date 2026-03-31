import { useEffect, useState } from 'react'
import { ProjectCard } from '../components/ProjectCard'
import { RecommendationCard } from '../components/RecommendationCard'
import { RiskCard } from '../components/RiskCard'
import { TaskList } from '../components/TaskList'
import { Modal } from '../components/ui/Modal'
import { useProactiveRules } from '../hooks/useProactiveRules'
import { useProjectMutations, useProjects } from '../hooks/useProjects'
import { useRecommender } from '../hooks/useRecommender'
import { useRiskDetection, useRisks } from '../hooks/useRisks'
import { useTaskMutations, useTasks } from '../hooks/useTasks'
import { useTriggerProactive } from '../hooks/useTriggerProactive'
import { useUploadDocument } from '../hooks/useUploadDocument'
import type { Project, Recommendation, Risk, Task } from '../types'

export function DashboardPage() {
  const { data: projects = [] } = useProjects()
  const { data: tasks = [] } = useTasks()
  const { data: risks = [] } = useRisks()
  const { data: proactiveRules = [] } = useProactiveRules()
  const [selectedTaskId, setSelectedTaskId] = useState<string | undefined>(undefined)
  const [selectedRuleId, setSelectedRuleId] = useState<string | undefined>(undefined)
  const [recommendation, setRecommendation] = useState<Recommendation | undefined>(undefined)
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const [selectedRisk, setSelectedRisk] = useState<Risk | null>(null)
  const [isUploadOpen, setIsUploadOpen] = useState(false)
  const recommenderMutation = useRecommender()
  const { createTask: createTaskMutation } = useTaskMutations()
  const { createProject: createProjectMutation } = useProjectMutations()
  const { detectFromTask } = useRiskDetection()
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
          onClick={() => setIsUploadOpen(true)}
        >
          Загрузить документ
        </button>
        <button
          type="button"
          className="rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-500"
          onClick={() => createTaskMutation.mutate({ title: `Quick task ${new Date().toLocaleTimeString()}` })}
        >
          Создать задачу
        </button>
        <button
          type="button"
          className="rounded-lg bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-500"
          onClick={() => createProjectMutation.mutate({ name: `Project ${projects.length + 1}`, project_type: 'general', stage: 'planned' })}
        >
          Создать проект
        </button>
        <button
          type="button"
          className="rounded-lg bg-violet-600 px-3 py-2 text-sm font-medium text-white hover:bg-violet-500"
          onClick={() => proactiveMutation.mutate()}
          disabled={!selectedTaskId || !selectedRuleId}
        >
          Триггер proactive ping
        </button>
        <button
          type="button"
          className="rounded-lg bg-cyan-700 px-3 py-2 text-sm font-medium text-white hover:bg-cyan-600"
          onClick={() => {
            if (!selectedTaskId) return
            recommenderMutation.mutate(selectedTaskId, {
              onSuccess: (data) => setRecommendation(data),
            })
          }}
          disabled={!selectedTaskId}
        >
          Получить рекомендацию
        </button>
        <button
          type="button"
          className="rounded-lg bg-amber-500 px-3 py-2 text-sm font-medium text-white hover:bg-amber-400"
          onClick={() => selectedTaskId && detectFromTask.mutate(selectedTaskId)}
          disabled={!selectedTaskId}
        >
          Detect risk by task
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
            <ProjectCard key={project.id} project={project} onClick={setSelectedProject} />
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold text-slate-900">Tasks</h2>
        <TaskList tasks={tasks.slice(0, 6)} onTaskClick={setSelectedTask} />
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold text-slate-900">Risks</h2>
        <div className="grid gap-3 md:grid-cols-2">
          {risks.slice(0, 4).map((risk) => (
            <RiskCard key={risk.id} risk={risk} onClick={setSelectedRisk} />
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold text-slate-900">Recommendation</h2>
        <RecommendationCard recommendation={recommendation} isLoading={recommenderMutation.isPending} />
      </section>

      <Modal isOpen={isUploadOpen} onClose={() => setIsUploadOpen(false)} title="Загрузка документа">
        <input
          type="file"
          className="block w-full rounded-lg border border-slate-300 p-2 text-sm"
          onChange={(event) => {
            const file = event.target.files?.[0]
            if (!file) return
            uploadMutation.mutate(file, { onSuccess: () => setIsUploadOpen(false) })
          }}
        />
      </Modal>

      <Modal isOpen={Boolean(selectedProject)} onClose={() => setSelectedProject(null)} title="Детали проекта">
        {selectedProject ? <p className="text-sm text-slate-700">{selectedProject.name}</p> : null}
      </Modal>
      <Modal isOpen={Boolean(selectedTask)} onClose={() => setSelectedTask(null)} title="Детали задачи">
        {selectedTask ? <p className="text-sm text-slate-700">{selectedTask.title}</p> : null}
      </Modal>
      <Modal isOpen={Boolean(selectedRisk)} onClose={() => setSelectedRisk(null)} title="Детали риска">
        {selectedRisk ? <p className="text-sm text-slate-700">{selectedRisk.title}</p> : null}
      </Modal>
    </main>
  )
}
