import type { Project } from '../types'

interface ProjectCardProps {
  project: Project
}

export function ProjectCard({ project }: ProjectCardProps) {
  return (
    <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h3 className="text-base font-semibold text-slate-900">{project.name}</h3>
      <p className="mt-2 text-sm text-slate-600">Type: {project.project_type}</p>
      <p className="text-sm text-slate-600">Stage: {project.stage}</p>
    </article>
  )
}
