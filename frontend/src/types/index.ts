export type UUID = string

export interface Project {
  id: UUID
  name: string
  project_type: string
  stage: string
  custom_fields: Record<string, unknown>
}

export interface Task {
  id: UUID
  title: string
  description: string
  status: 'to-do' | 'in-progress' | 'blocked' | 'done' | 'canceled'
  priority: 'low' | 'medium' | 'high' | 'critical'
  estimated_hours: number
  due_at: string | null
  dependency_ids: string[]
  tags: string[]
  project_id: UUID | null
  assignee_id: UUID | null
}

export interface Risk {
  id: string
  title: string
  probability: number
  impact: number
  mitigation_plan: string
  status: string
  severity: 'high' | 'medium' | 'low'
  source: 'task' | 'document' | 'message'
  project_id: string | null
  task_id: string | null
}

export interface RecommendationCandidate {
  user_id: string
  full_name: string
  competency: number
  load: number
  total_score: number
  explanation: string
}

export interface Recommendation {
  recommended_user_id: string | null
  recommended_user_name: string | null
  reason: string
  candidates: RecommendationCandidate[]
  llm_notes: string | null
  metadata: Record<string, unknown>
}

export interface ProactiveTriggerResponse {
  sent: boolean
  ping: {
    rule_id: string
    task_id: string
    target_user_id: string | null
    message: string
  }
}

export interface ProactiveRule {
  id: string
  name: string
  trigger_type: string
  action_type: string
  config: Record<string, unknown>
  buttons: Array<Record<string, unknown>>
  enabled: boolean
  created_at: string
  updated_at: string
}
