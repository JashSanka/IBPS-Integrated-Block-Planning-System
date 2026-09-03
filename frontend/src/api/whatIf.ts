import { apiFetch } from './client';
import type { WhatIfReplanResponse, EmergencyTaskInput } from './types';

export const runWhatIfReplan = (task: EmergencyTaskInput) =>
  apiFetch<WhatIfReplanResponse>('/plans/what-if', {
    method: 'POST',
    body: JSON.stringify({ task }),
  });
