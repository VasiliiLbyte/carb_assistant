import type { Project } from '../types'
import type { ReactNode } from 'react'

interface ProjectCardProps {
  project: Project
  onClick?: (project: Project) => void
  actionSlot?: ReactNode
}

export function ProjectCard({ project, onClick, actionSlot }: ProjectCardProps) {
  return (
    <article
      className={`rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition ${
        onClick ? 'cursor-pointer hover:border-indigo-300 hover:shadow-md' : ''
      }`}
      onClick={() => onClick?.(project)}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={(event) => {
        if (!onClick) return
        if (event.key === 'Enter' || event.key === ' ') {
          onClick(project)
        }
      }}
    >
      <h3 className="text-base font-semibold text-slate-900">{project.name}</h3>
      <p className="mt-2 text-sm text-slate-600">Type: {project.project_type}</p>
      <p className="text-sm text-slate-600">Stage: {project.stage}</p>
      {actionSlot ? <div className="mt-3" onClick={(event) => event.stopPropagation()}>{actionSlot}</div> : null}
    </article>
  )
}
