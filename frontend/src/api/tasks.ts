import { apiFetch } from './client';
import type { TaskItemResponse, TaskDetailResponse } from './types';

export const fetchTasks = (params?: Record<string, string>) => {
  const qs = params ? '?' + new URLSearchParams(params).toString() : '';
  return apiFetch<TaskItemResponse[]>(`/tasks${qs}`);
};

export const fetchTaskDetail = (taskId: string) =>
  apiFetch<TaskDetailResponse>(`/tasks/${encodeURIComponent(taskId)}`);
