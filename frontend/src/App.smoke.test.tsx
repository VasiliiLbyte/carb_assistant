import { describe, expect, it, vi } from 'vitest'
import { renderToString } from 'react-dom/server'
import { DashboardPage } from './pages/DashboardPage'

vi.mock('./hooks/useProjects', () => ({
  useProjects: () => ({ data: [{ id: '1', name: 'Alpha', project_type: 'general', stage: 'planned', custom_fields: {} }] }),
  useProjectMutations: () => ({ createProject: { mutate: vi.fn() } }),
}))
vi.mock('./hooks/useTasks', () => ({
  useTasks: () => ({ data: [{ id: '1', title: 'Task', description: '', status: 'to-do', priority: 'medium', estimated_hours: 1, due_at: null, dependency_ids: [], tags: [], project_id: null, assignee_id: null }] }),
  useTaskMutations: () => ({ createTask: { mutate: vi.fn() } }),
}))
vi.mock('./hooks/useRisks', () => ({
  useRisks: () => ({ data: [{ id: '1', title: 'Risk', probability: 1, impact: 1, mitigation_plan: '', status: 'open', severity: 'low', source: 'message', project_id: null, task_id: null }] }),
  useRiskDetection: () => ({ detectFromTask: { mutate: vi.fn() } }),
}))
vi.mock('./hooks/useProactiveRules', () => ({ useProactiveRules: () => ({ data: [{ id: 'rule1', name: 'Rule 1' }] }) }))
vi.mock('./hooks/useRecommender', () => ({ useRecommender: () => ({ mutateAsync: vi.fn(), isPending: false }) }))
vi.mock('./hooks/useTriggerProactive', () => ({ useTriggerProactive: () => ({ mutate: vi.fn() }) }))
vi.mock('./hooks/useUploadDocument', () => ({ useUploadDocument: () => ({ mutate: vi.fn() }) }))

describe('Frontend smoke', () => {
  it('renders dashboard and key actions', () => {
    const html = renderToString(<DashboardPage />)

    expect(html).toContain('Projects')
    expect(html).toContain('Создать задачу')
    expect(html).toContain('Загрузить документ')
    expect(html).toContain('Триггер proactive ping')
    expect(html).toContain('Получить рекомендацию')
  })
})
