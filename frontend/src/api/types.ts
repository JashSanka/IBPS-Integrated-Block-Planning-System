// API types mirroring backend Pydantic schemas

export interface HealthResponse {
  status: string;
  system: string;
  version: string;
  data_mode: string;
  description: string;
  human_in_the_loop_notice: string;
}

export type PriorityBand = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'ROUTINE';
export type Department = 'ENGINEERING' | 'S&T' | 'TRD';
export type TaskStatus = 'SCHEDULED' | 'UNSCHEDULED' | 'PENDING';
export type SolverStatus = 'OPTIMAL' | 'FEASIBLE' | 'INFEASIBLE' | 'UNKNOWN' | 'ERROR';
export type TrafficDensity = 'HIGH' | 'MEDIUM' | 'LOW';

// ─── Dashboard ─────────────────────────────────────────────────────────────
export interface MetricDetail {
  metric_name: string;
  display_name: string;
  baseline_value: number;
  optimized_value: number;
  delta: number;
  percentage_change: number;
  unit: string;
  higher_is_better: boolean;
  label: string;
}

export interface TaskDashboardSummary {
  total: number;
  critical: number;
  high: number;
  medium: number;
  routine: number;
  scheduled_baseline: number;
  scheduled_optimized: number;
  unscheduled_optimized: number;
}

export interface BlockDashboardSummary {
  available: number;
  used_baseline: number;
  used_optimized: number;
  total_possession_hours_baseline: number;
  total_possession_hours_optimized: number;
}

export interface DashboardSummaryResponse {
  data_badge: string;
  positioning_statement: string;
  active_dataset: string;
  tasks: TaskDashboardSummary;
  blocks: BlockDashboardSummary;
  metrics_summary: MetricDetail[];
  departments: string[];
  corridors: string[];
  last_plan_generated_at: string | null;
}

// ─── Tasks ──────────────────────────────────────────────────────────────────
export interface TaskItemResponse {
  task_id: string;
  department: Department;
  asset_id: string;
  asset_type: string;
  corridor_id: string;
  location: string;
  defect_type: string;
  severity: string;
  criticality: number;
  safety_risk: number;
  overdue_days: number;
  estimated_duration_min: number;
  crew_required: number;
  resource_requirements: string[];
  precedence: string[];
  incompatible_tasks: string[];
  earliest_start: string;
  deadline: string;
  status: TaskStatus;
  traffic_criticality: number;
  priority_score: number | null;
  priority_band: PriorityBand | null;
  score_breakdown: Record<string, number> | null;
  scheduled_block_id: string | null;
  scheduled_start: string | null;
  scheduled_end: string | null;
  assignment_explanation: string | null;
}

export interface CandidateFeasibilityItem {
  block_id: string;
  corridor_id: string;
  start_time: string;
  end_time: string;
  duration_minutes: number;
  feasible: boolean;
  reasons: string[];
}

export interface TaskDetailResponse {
  task: TaskItemResponse;
  feasible_blocks_count: number;
  feasible_blocks: string[];
  candidate_evaluations: CandidateFeasibilityItem[];
  precedence_tasks_details: Record<string, unknown>[];
  incompatible_tasks_details: Record<string, unknown>[];
  current_scheduled_block: Record<string, unknown> | null;
}

// ─── Blocks ─────────────────────────────────────────────────────────────────
export interface BlockItemResponse {
  block_id: string;
  corridor_id: string;
  start_time: string;
  end_time: string;
  duration_minutes: number;
  duration_hours: number;
  available_capacity: number;
  resource_capacity: number;
  safety_constraints: string[];
  permitted_departments: Department[];
  traffic_density: TrafficDensity;
  used_slots: number;
  used_crew: number;
  slot_utilization_pct: number;
  crew_utilization_pct: number;
  assigned_departments: Department[];
  is_multi_department_clubbed: boolean;
  scheduled_tasks_count: number;
  train_disruption_cost: number;
}

export interface BlockTaskAssignmentSummary {
  task_id: string;
  department: Department;
  defect_type: string;
  asset_id: string;
  priority_score: number;
  priority_band: string;
  crew_required: number;
  estimated_duration_min: number;
  scheduled_start: string;
  scheduled_end: string;
  explanation: string;
}

export interface BlockTrainImpactSummary {
  train_id: string;
  train_type: string;
  direction: string;
  start_time: string;
  end_time: string;
  operational_priority: number;
  disruption_penalty: number;
  is_hard_conflict: boolean;
}

export interface BlockFreightImpactSummary {
  time_window: string;
  expected_goods_trains: number;
  probability: number;
  traffic_density: string;
}

export interface BlockDetailResponse {
  block: BlockItemResponse;
  assigned_tasks: BlockTaskAssignmentSummary[];
  train_conflicts: BlockTrainImpactSummary[];
  freight_forecasts: BlockFreightImpactSummary[];
  clubbing_status_description: string;
  safety_clearance_notes: string[];
}

// ─── Plans ──────────────────────────────────────────────────────────────────
export interface PlanMetrics {
  plan_id: string;
  total_tasks: number;
  scheduled_tasks?: number;
  unscheduled_tasks?: number;
  scheduled_tasks_count?: number;
  unscheduled_tasks_count?: number;
  total_critical_tasks?: number;
  critical_tasks_completed: number;
  total_priority_score?: number;
  completed_priority_score?: number;
  priority_score_completion_pct: number;
  cross_department_clubbed_blocks?: number;
  multi_department_clubbed_blocks_count?: number;
  average_block_utilization_pct: number;
  blocks_used_count?: number;
  total_block_hours: number;
  train_conflict_count?: number;
  train_conflicts_count?: number;
  total_train_disruption_penalty?: number;
  goods_traffic_penalty?: number;
  simulated_asset_availability_pct: number;
}

export interface ScheduledTask {
  task_id: string;
  block_id: string;
  scheduled_start: string;
  scheduled_end: string;
  explanation: string;
}

export interface PlanResponse {
  plan_id: string;
  plan_type: string;
  horizon: string;
  generated_at: string;
  solver_status: SolverStatus;
  objective_value: number | null;
  blocks_used: string[];
  scheduled_tasks_count: number;
  unscheduled_tasks_count: number;
  scheduled_tasks: ScheduledTask[];
  unscheduled_tasks: string[];
  metrics: PlanMetrics;
  objective_breakdown: Record<string, number> | null;
  warnings: string[];
}

export interface PlanComparisonResponse {
  baseline_plan_id: string;
  optimized_plan_id: string;
  baseline_metrics: PlanMetrics;
  optimized_metrics: PlanMetrics;
  comparisons: MetricDetail[];
  human_in_the_loop_positioning: string;
}

// ─── What-If ─────────────────────────────────────────────────────────────────
export interface EmergencyTaskInput {
  task_id: string;
  department: string;
  asset_id: string;
  asset_type: string;
  corridor_id: string;
  location: string;
  defect_type: string;
  severity: string;
  criticality: number;
  safety_risk: number;
  duration_minutes: number;
  crew_required: number;
  traffic_criticality: number;
  incompatible_tasks: string[];
}

export interface ReplanTaskChange {
  task_id: string;
  action: string;
  previous_block_id: string | null;
  new_block_id: string | null;
  reason: string;
}

export interface ReplanDiffResponse {
  previous_plan_id: string;
  new_plan_id: string;
  emergency_task_id: string;
  tasks_added: ReplanTaskChange[];
  tasks_moved: ReplanTaskChange[];
  tasks_displaced: ReplanTaskChange[];
  tasks_unchanged: string[];
  metric_deltas: MetricDetail[];
}

export interface WhatIfReplanResponse {
  status: string;
  before: PlanResponse;
  after: PlanResponse;
  diff: ReplanDiffResponse;
  kpi_impact: MetricDetail[];
}

// ─── Diagnostics ─────────────────────────────────────────────────────────────
export interface DiagnosticsResponse {
  total_candidate_pairs: number;
  feasible_pairs_count: number;
  rejected_pairs_count: number;
  rejected_reasons_tally: Record<string, number>;
  objective_contributions: Record<string, number>;
  blocks_used_count: number;
  department_combinations_by_block: Record<string, string[]>;
  unscheduled_tasks_diagnostics: Record<string, string[]>;
  solver_wall_time_seconds: number;
  human_in_the_loop_positioning: string;
}

// ─── Dataset ─────────────────────────────────────────────────────────────────
export interface DatasetSummaryResponse {
  active_dataset: string;
  description: string;
  task_count: number;
  critical_task_count: number;
  block_count: number;
  train_count: number;
  corridor_count: number;
  corridors: string[];
  departments: string[];
}
