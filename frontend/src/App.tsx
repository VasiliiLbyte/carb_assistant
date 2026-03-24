import { Link, Route, Routes } from 'react-router-dom'
import { DashboardPage } from './pages/DashboardPage'
import { ProjectsPage } from './pages/ProjectsPage'
import { TasksPage } from './pages/TasksPage'
import { DocumentsPage } from './pages/DocumentsPage'
import { RisksPage } from './pages/RisksPage'
import { UsersPage } from './pages/UsersPage'
import { AIRecommendationsPage } from './pages/AIRecommendationsPage'
import { ProactiveRulesPage } from './pages/ProactiveRulesPage'

export default function App() {
  return (
    <div style={{ padding: 16 }}>
      <nav style={{ display: 'flex', gap: 12, marginBottom: 12 }}>
        <Link to="/">Dashboard</Link>
        <Link to="/projects">Projects</Link>
        <Link to="/tasks">Tasks</Link>
        <Link to="/documents">Documents</Link>
        <Link to="/risks">Risks</Link>
        <Link to="/users">Users</Link>
        <Link to="/ai">AI Log</Link>
        <Link to="/proactive">Proactive</Link>
      </nav>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/projects" element={<ProjectsPage />} />
        <Route path="/tasks" element={<TasksPage />} />
        <Route path="/documents" element={<DocumentsPage />} />
        <Route path="/risks" element={<RisksPage />} />
        <Route path="/users" element={<UsersPage />} />
        <Route path="/ai" element={<AIRecommendationsPage />} />
        <Route path="/proactive" element={<ProactiveRulesPage />} />
      </Routes>
    </div>
  )
}
