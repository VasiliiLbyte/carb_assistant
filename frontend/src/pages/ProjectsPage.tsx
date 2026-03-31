import { ProjectCard } from '../components/ProjectCard'
import { useProjects } from '../hooks/useProjects'

export function ProjectsPage() {
  const { data: projects = [], isLoading } = useProjects()

  if (isLoading) {
    return <p className="text-sm text-slate-500">Loading projects...</p>
  }

  return (
    <div className="grid gap-3 md:grid-cols-2">
      {projects.map((project) => (
        <ProjectCard key={project.id} project={project} />
      ))}
    </div>
  )
}
