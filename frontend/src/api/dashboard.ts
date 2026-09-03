import { apiFetch } from './client';
import type { HealthResponse, DashboardSummaryResponse } from './types';

export const fetchHealth = () =>
  apiFetch<HealthResponse>('/health');

export const fetchDashboard = () =>
  apiFetch<DashboardSummaryResponse>('/dashboard');
