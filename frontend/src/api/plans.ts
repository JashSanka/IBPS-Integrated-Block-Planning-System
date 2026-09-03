import { apiFetch } from './client';
import type { PlanResponse, PlanComparisonResponse } from './types';

export const generateBaseline = (horizon = 'WEEKLY') =>
  apiFetch<PlanResponse>(`/plans/baseline?horizon=${horizon}`, { method: 'POST' });

export const generateOptimized = (body: { horizon: string; objective_profile: string }) =>
  apiFetch<PlanResponse>('/plans/optimize', {
    method: 'POST',
    body: JSON.stringify(body),
  });

export const fetchPlanComparison = () =>
  apiFetch<PlanComparisonResponse>('/plans/comparison');

export const fetchLatestPlan = (type: 'optimized' | 'baseline' = 'optimized') =>
  apiFetch<PlanResponse>(`/plans/latest?plan_type=${type}`);
