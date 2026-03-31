import { apiClient } from './client'
import type {
  Project,
  ProjectPayload,
  ProactiveRule,
  ProactiveTriggerResponse,
  Recommendation,
  Risk,
  RiskDetectionResult,
  Task,
  TaskPayload,
} from '../types'

export const getProjects = async (): Promise<Project[]> => {
  const { data } = await apiClient.get<Project[]>('/projects')
  return data
}

export const createProject = async (payload: ProjectPayload): Promise<Project> => {
  const { data } = await apiClient.post<Project>('/projects', payload)
  return data
}

export const updateProject = async (projectId: string, payload: Partial<ProjectPayload>): Promise<Project> => {
  const { data } = await apiClient.put<Project>(`/projects/${projectId}`, payload)
  return data
}

export const deleteProject = async (projectId: string): Promise<void> => {
  await apiClient.delete(`/projects/${projectId}`)
}

export const getTasks = async (): Promise<Task[]> => {
  const { data } = await apiClient.get<Task[]>('/tasks')
  return data
}

export const createTask = async (payload: Partial<Task> & { title: string }): Promise<Task> => {
  const { data } = await apiClient.post<Task>('/tasks', payload)
  return data
}

export const updateTask = async (taskId: string, payload: Partial<TaskPayload>): Promise<Task> => {
  const { data } = await apiClient.put<Task>(`/tasks/${taskId}`, payload)
  return data
}

export const deleteTask = async (taskId: string): Promise<void> => {
  await apiClient.delete(`/tasks/${taskId}`)
}

export const getRisks = async (): Promise<Risk[]> => {
  const { data } = await apiClient.get<Risk[]>('/risks')
  return data
}

export const getRecommendation = async (taskId: string): Promise<Recommendation> => {
  const { data } = await apiClient.post<Recommendation>('/recommender/recommend', { task_id: taskId })
  return data
}

export const uploadDocument = async (file: File): Promise<{ file_key: string; filename: string }> => {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await apiClient.post<{ file_key: string; filename: string }>('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export const triggerProactive = async (ruleId: string, taskId: string): Promise<ProactiveTriggerResponse> => {
  const { data } = await apiClient.post<ProactiveTriggerResponse>('/proactive/trigger', {
    rule_id: ruleId,
    task_id: taskId,
  })
  return data
}

export const getProactiveRules = async (): Promise<ProactiveRule[]> => {
  const { data } = await apiClient.get<ProactiveRule[]>('/proactive/rules')
  return data
}

export const detectRisksFromTask = async (taskId: string): Promise<RiskDetectionResult> => {
  const { data } = await apiClient.post<RiskDetectionResult>('/risks/detect-from-task', { task_id: taskId })
  return data
}

export const detectRisksFromDocument = async (
  documentKey: string,
  projectId?: string,
): Promise<RiskDetectionResult> => {
  const { data } = await apiClient.post<RiskDetectionResult>('/risks/detect-from-document', {
    document_key: documentKey,
    project_id: projectId,
  })
  return data
}

export const detectRisksFromMessage = async (message: string, projectId?: string): Promise<RiskDetectionResult> => {
  const { data } = await apiClient.post<RiskDetectionResult>('/risks/detect-from-message', {
    message,
    project_id: projectId,
  })
  return data
}
