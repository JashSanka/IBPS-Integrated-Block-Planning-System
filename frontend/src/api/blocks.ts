import { apiFetch } from './client';
import type { BlockItemResponse, BlockDetailResponse } from './types';

export const fetchBlocks = (corridor?: string) => {
  const qs = corridor ? `?corridor=${encodeURIComponent(corridor)}` : '';
  return apiFetch<BlockItemResponse[]>(`/blocks${qs}`);
};

export const fetchBlockDetail = (blockId: string) =>
  apiFetch<BlockDetailResponse>(`/blocks/${encodeURIComponent(blockId)}`);
