const REASON_LABELS: Record<string, string> = {
  TRAIN_CONFLICT: 'Conflicts with a scheduled train movement',
  CORRIDOR_MISMATCH: 'Corridor does not match',
  DEPARTMENT_NOT_PERMITTED: 'Department not permitted on this block',
  SAFETY_CONSTRAINT_MISSING: 'Safety constraint not satisfied',
  DURATION_EXCEEDED: 'Task duration exceeds block window',
  COMPETED_OUT_BY_HIGHER_PRIORITY_TASKS: 'Displaced by higher-priority tasks competing for the same block(s)',
  FEASIBLE_CANDIDATE: 'Feasible candidate',
};

const DEFECT_LABELS: Record<string, string> = {
  SUDDEN_TRANSVERSE_RAIL_CRACK: 'Sudden Transverse Rail Crack',
  DIGITAL_AXLE_COUNTER_RESET_DRIFT: 'Digital Axle Counter Reset Drift',
  SEVERE_RAIL_FRACTURE: 'Severe Rail Fracture',
  OHE_CANTILEVER_INSULATOR_FLASH: 'OHE Cantilever Insulator Flashover',
  TURNOUT_SWITCH_RAIL_WEAR: 'Turnout Switch Rail Wear',
  SIGNAL_CABLE_INSULATION_FAIL: 'Signal Cable Insulation Failure',
  TRACK_GEOMETRY_TWIST_DEFECT: 'Track Geometry Twist Defect',
  POWER_BLOCK_AVAILABLE: 'Power Block Available',
};

export const KNOWN_DEFECT_TYPES = Object.keys(DEFECT_LABELS);

export function humanizeDefect(code: string): string {
  if (!code) return '';
  return DEFECT_LABELS[code] ?? humanizeLabel(code);
}

export function humanizeReason(code: string): string {
  if (!code) return '';
  const [rawCode, detail] = code.split(':', 2);
  const label = REASON_LABELS[rawCode.trim()] ?? humanizeLabel(rawCode);
  return detail ? `${label}: ${detail.trim()}` : label;
}

export function humanizePruneReason(code: string): string {
  if (!code) return '';
  return REASON_LABELS[code] ?? humanizeLabel(code);
}

export function humanizeLabel(value: string): string {
  if (!value) return '';
  return value
    .replaceAll('_', ' ')
    .toLowerCase()
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

export function formatUnscheduledReason(reason: string): { text: string; blocks: string[] } {
  const [code] = reason.split(' ', 1);
  const blocks = [...reason.matchAll(/BLK-[A-Z0-9-]+/g)].map((match) => match[0]);
  if (code === 'COMPETED_OUT_BY_HIGHER_PRIORITY_TASKS') {
    return {
      text: 'Displaced by higher-priority work competing for the same corridor blocks',
      blocks,
    };
  }
  return { text: humanizeReason(reason), blocks };
}

export function departmentCode(department: string): string {
  if (department === 'ENGINEERING') return 'ENG';
  return department;
}

export function titleStatus(value: string): string {
  return humanizeLabel(value);
}

