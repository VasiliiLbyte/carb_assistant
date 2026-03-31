import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { RequireAuth } from './auth/RequireAuth'
import { Sidebar } from './components/Sidebar'
import { ToastProvider } from './components/ToastProvider'
import { DashboardPage } from './pages/DashboardPage'
import { ProjectsPage } from './pages/ProjectsPage'
import { TasksPage } from './pages/TasksPage'
import { DocumentsPage } from './pages/DocumentsPage'
import { RisksPage } from './pages/RisksPage'
import { SettingsPage } from './pages/SettingsPage'
import { LoginPage } from './pages/LoginPage'

function AppShell() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 p-4 lg:flex-row">
        <Sidebar />
        <div className="flex-1">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/projects" element={<ProjectsPage />} />
            <Route path="/tasks" element={<TasksPage />} />
            <Route path="/documents" element={<DocumentsPage />} />
            <Route path="/risks" element={<RisksPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </div>
    </div>
  )
}

export default function App() {
  const location = useLocation()

  // Hard override for login route to avoid any nested-route mismatch.
  if (location.pathname === '/login') {
    return (
      <ToastProvider>
        <LoginPage />
      </ToastProvider>
    )
  }

  return (
    <ToastProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/*"
          element={
            <RequireAuth>
              <AppShell />
            </RequireAuth>
          }
        />
      </Routes>
    </ToastProvider>
  )
}
