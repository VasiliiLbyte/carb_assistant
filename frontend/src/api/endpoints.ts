import { apiClient } from './client'
import type { Project, Recommendation, Risk, Task, ProactiveRule, ProactiveTriggerResponse } from '../types'

export const getProjects = async (): Promise<Project[]> => {
  const { data } = await apiClient.get<Project[]>('/projects')
  return data
}

export const getTasks = async (): Promise<Task[]> => {
  const { data } = await apiClient.get<Task[]>('/tasks')
  return data
}

export const createTask = async (payload: Partial<Task> & { title: string }): Promise<Task> => {
  const { data } = await apiClient.post<Task>('/tasks', payload)
  return data
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
