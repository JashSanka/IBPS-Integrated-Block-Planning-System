import { AlertCircle, Loader2 } from 'lucide-react';
import type { ReactNode } from 'react';
import { departmentCode, titleStatus } from '../lib/labels';

export type MetricStripItem = {
  label: string;
  value: ReactNode;
  unit?: string;
  delta?: number;
  higherBetter?: boolean;
  tone?: 'default' | 'success' | 'warning' | 'danger' | 'muted' | 'accent';
};

export function Loader({ label = 'Loading data...' }: { label?: string }) {
  return (
    <div className="state-shell">
      <Loader2 size={20} className="spin" />
      <div>
        <strong>{label}</strong>
        <p>Waiting for the planning service response.</p>
      </div>
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="state-shell">
      <AlertCircle size={20} className="text-accent" />
      <div>
        <strong>Unable to load data.</strong>
        <p>{message}</p>
      </div>
    </div>
  );
}

export function EmptyState({ label, detail = 'No records are available for the current view.' }: { label: string; detail?: string }) {
  return (
    <div className="state-shell">
      <div>
        <strong>{label}</strong>
        <p>{detail}</p>
      </div>
    </div>
  );
}

export function Panel({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <section className={`panel ${className}`}>{children}</section>;
}

export const Card = Panel;

export function PanelHeader({ title, sub, right }: { title: string; sub?: string; right?: ReactNode }) {
  return (
    <div className="panel-header">
      <div>
        <div className="panel-title-main">{title}</div>
        {sub && <div className="panel-subtitle">{sub}</div>}
      </div>
      {right && <div className="panel-action">{right}</div>}
    </div>
  );
}

export const CardHeader = PanelHeader;

/* Swiss Hero Metric or Metric Strip */
export function HeroMetric({ label, value, unit, caption }: { label: string; value: ReactNode; unit?: string; caption?: string }) {
  return (
    <div className="hero-metric-block">
      <div className="hero-metric-value">
        {value}
        {unit && <span className="hero-metric-unit">{unit}</span>}
      </div>
      <div className="hero-metric-label">{label}</div>
      {caption && <div className="hero-metric-caption">{caption}</div>}
    </div>
  );
}

export function MetricStrip({ items, compact = false }: { items: MetricStripItem[]; compact?: boolean }) {
  return (
    <div className={`metric-strip ${compact ? 'compact' : ''}`}>
      {items.map((item) => {
        return (
          <div className="metric-strip-item" key={item.label}>
            <span className="metric-label">{item.label}</span>
            <strong className={`metric-value ${item.tone === 'danger' ? 'text-accent' : ''}`}>
              {item.value}
              {item.unit && <small>{item.unit}</small>}
            </strong>
            {item.delta !== undefined && (
              <span className={`metric-delta ${item.delta < 0 && item.higherBetter !== false ? 'text-accent' : ''}`}>
                {item.delta === 0 ? '0.0%' : item.delta > 0 ? `+${item.delta.toFixed(1)}%` : `${item.delta.toFixed(1)}%`}
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
}

/* Bracketed Department Badge: [ENG], [S&T], [TRD] */
export function DeptBadge({ dept }: { dept: string }) {
  const code = departmentCode(dept);
  return <span className="dept-bracket">[{code}]</span>;
}

/* Swiss Text-Based Priority Badge */
export function PriorityBadge({ band }: { band: string | null }) {
  if (!band || band === 'ROUTINE') return <span className="priority-text routine">Routine</span>;
  if (band === 'CRITICAL') {
    return (
      <span className="priority-text critical">
        <span className="red-square" />
        CRITICAL
      </span>
    );
  }
  if (band === 'HIGH') return <span className="priority-text high">HIGH</span>;
  return <span className="priority-text medium">{titleStatus(band)}</span>;
}

/* Swiss Text-Based Status Tag */
export function StatusBadge({ status }: { status: string }) {
  const isCritical = status === 'CRITICAL' || status === 'EMERGENCY' || status === 'INFEASIBLE';
  const isHigh = status === 'HIGH';
  return (
    <span className={`swiss-status ${isCritical ? 'critical' : isHigh ? 'high' : 'normal'}`}>
      {isCritical && <span className="red-square" />}
      {titleStatus(status)}
    </span>
  );
}

export function StatusText({ status, danger = false }: { status: string; danger?: boolean }) {
  return <span className={`swiss-status ${danger ? 'critical' : 'normal'}`}>{titleStatus(status)}</span>;
}

export function UtilBar({ pct }: { pct: number }) {
  return (
    <div className="util-bar">
      <div className="util-track">
        <span className={`util-fill ${pct > 90 ? 'critical' : ''}`} style={{ width: `${Math.min(Math.max(pct, 0), 100)}%` }} />
      </div>
      <strong className="mono">{pct.toFixed(0)}%</strong>
    </div>
  );
}

export function LabeledBarList({ values, signed = false, humanize }: { values: Record<string, number>; signed?: boolean; humanize?: (key: string) => string }) {
  const max = Math.max(1, ...Object.values(values).map((value) => Math.abs(value)));
  return (
    <div className={`labeled-bars ${signed ? 'diverging' : ''}`}>
      {Object.entries(values).map(([key, value]) => {
        const pct = Math.min(100, Math.max(2, (Math.abs(value) / max) * (signed ? 48 : 100)));
        const width = `${pct}%`;
        const isNegative = value < 0;
        return (
          <div className="labeled-bar-row" key={key}>
            <div className="bar-name">{humanize ? humanize(key) : titleStatus(key)}</div>
            <div className="bar-axis">
              {signed && <span className="zero-line" />}
              <span
                className={`bar-fill ${isNegative ? 'negative' : 'positive'}`}
                style={signed ? (isNegative ? { right: '50%', width } : { left: '50%', width }) : { left: 0, width }}
              />
            </div>
            <div className="bar-value mono">{signed && value > 0 ? '+' : ''}{value.toFixed(value % 1 ? 1 : 0)}</div>
          </div>
        );
      })}
    </div>
  );
}

export function InsightList({ items }: { items: string[] }) {
  return (
    <ul className="insight-list">
      {items.map((item) => (
        <li key={item}>
          <span className="bullet-dash">—</span>
          <p>{item}</p>
        </li>
      ))}
    </ul>
  );
}

export function SystemIndicators({ dataset = 'demo_fixture', status = 'ok', badge = 'SYNTHETIC DATA' }: { dataset?: string; status?: string; badge?: string }) {
  return (
    <div className="system-indicators">
      <span className="dataset-tag">DATASET: <strong className="mono">{dataset}</strong></span>
      <span className="synthetic-tag">{badge}</span>
      <span className="backend-tag">
        <span className="backend-square" />
        BACKEND {status.toUpperCase()}
      </span>
    </div>
  );
}


