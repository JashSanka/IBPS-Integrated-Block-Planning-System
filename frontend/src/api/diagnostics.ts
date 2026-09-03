import { apiFetch } from './client';
import type { DiagnosticsResponse } from './types';

export const fetchDiagnostics = () =>
  apiFetch<DiagnosticsResponse>('/plans/diagnostics');
