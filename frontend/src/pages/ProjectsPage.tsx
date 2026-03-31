import { useMemo, useState } from 'react'
import { Modal } from '../components/ui/Modal'
import { ProjectCard } from '../components/ProjectCard'
import { useProjectMutations, useProjects } from '../hooks/useProjects'
import type { Project } from '../types'

export function ProjectsPage() {
  const { data: projects = [], isLoading } = useProjects()
  const { createProject, updateProject, deleteProject } = useProjectMutations()
  const [viewingProject, setViewingProject] = useState<Project | null>(null)
  const [editingProject, setEditingProject] = useState<Project | null>(null)
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [name, setName] = useState('')
  const [projectType, setProjectType] = useState('general')
  const [stage, setStage] = useState('planned')

  if (isLoading) {
    return <p className="text-sm text-slate-500">Loading projects...</p>
  }

  const modalFooter = useMemo(
    () => (
      <>
        <button
          type="button"
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
          onClick={() => {
            setViewingProject(null)
            setIsCreateOpen(false)
          }}
        >
          Отмена
        </button>
        <button
          type="button"
          className="rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-500"
          onClick={() => {
            if (!name.trim()) return
            const payload = { name: name.trim(), project_type: projectType, stage, custom_fields: {} }
            if (editingProject) {
              updateProject.mutate({ id: editingProject.id, payload })
            } else {
              createProject.mutate(payload)
            }
            setEditingProject(null)
            setIsCreateOpen(false)
            setName('')
          }}
        >
          Сохранить
        </button>
      </>
    ),
    [createProject, editingProject, name, projectType, stage, updateProject],
  )

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900">Проекты</h2>
        <button
          type="button"
          className="rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-500"
          onClick={() => {
            setViewingProject(null)
            setEditingProject(null)
            setName('')
            setProjectType('general')
            setStage('planned')
            setIsCreateOpen(true)
          }}
        >
          Создать проект
        </button>
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        {projects.map((project) => (
          <ProjectCard
            key={project.id}
            project={project}
            onClick={(current) => setViewingProject(current)}
            actionSlot={
              <div className="flex gap-2">
                <button
                  type="button"
                  className="rounded bg-slate-100 px-2 py-1 text-xs hover:bg-slate-200"
                  onClick={() => {
                    setEditingProject(project)
                    setName(project.name)
                    setProjectType(project.project_type)
                    setStage(project.stage)
                    setIsCreateOpen(true)
                  }}
                >
                  Редактировать
                </button>
                <button
                  type="button"
                  className="rounded bg-red-100 px-2 py-1 text-xs text-red-700 hover:bg-red-200"
                  onClick={() => deleteProject.mutate(project.id)}
                >
                  Удалить
                </button>
              </div>
            }
          />
        ))}
      </div>

      <Modal
        isOpen={isCreateOpen}
        onClose={() => {
          setIsCreateOpen(false)
          setEditingProject(null)
        }}
        title={editingProject ? 'Редактирование проекта' : 'Создание проекта'}
        footer={modalFooter}
      >
        <input
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          placeholder="Название проекта"
          value={name}
          onChange={(event) => setName(event.target.value)}
        />
        <input
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          placeholder="Тип проекта"
          value={projectType}
          onChange={(event) => setProjectType(event.target.value)}
        />
        <input
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          placeholder="Стадия"
          value={stage}
          onChange={(event) => setStage(event.target.value)}
        />
      </Modal>

      <Modal isOpen={Boolean(viewingProject)} onClose={() => setViewingProject(null)} title="Детали проекта">
        {viewingProject ? (
          <div className="space-y-2 text-sm">
            <p>
              <span className="font-medium text-slate-700">Название:</span> {viewingProject.name}
            </p>
            <p>
              <span className="font-medium text-slate-700">Тип:</span> {viewingProject.project_type}
            </p>
            <p>
              <span className="font-medium text-slate-700">Стадия:</span> {viewingProject.stage}
            </p>
          </div>
        ) : null}
      </Modal>
    </div>
  )
}
