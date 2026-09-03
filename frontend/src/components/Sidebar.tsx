import { NavLink } from 'react-router-dom';

const NAV_GROUPS = [
  {
    title: 'MONITOR',
    items: [
      { num: '01', to: '/dashboard', label: 'OVERVIEW' },
    ],
  },
  {
    title: 'PLAN',
    items: [
      { num: '02', to: '/planning', label: 'PLANNING' },
      { num: '03', to: '/tasks', label: 'MAINTENANCE TASKS' },
      { num: '04', to: '/blocks', label: 'BLOCK WINDOWS' },
      { num: '05', to: '/what-if', label: 'WHAT-IF REPLANNING' },
    ],
  },
  {
    title: 'TECHNICAL',
    items: [
      { num: '06', to: '/diagnostics', label: 'DIAGNOSTICS' },
    ],
  },
];

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-code">IBPS</div>
        <div className="brand-name">INTEGRATED BLOCK PLANNING SYSTEM</div>
        <div className="brand-sub">MINISTRY OF RAILWAYS — DECISION SUPPORT</div>
      </div>

      <nav className="sidebar-nav" aria-label="Primary navigation">
        {NAV_GROUPS.map((group) => (
          <div key={group.title} className="nav-group">
            <div className="nav-label">{group.title}</div>
            {group.items.map(({ num, to, label }) => (
              <NavLink key={to} to={to} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                <span className="nav-num mono">{num}</span>
                <span className="nav-text">{label}</span>
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar-status">
        <div className="nav-label">SYSTEM STATUS</div>
        <StatusLine label="API CONNECTED" />
        <StatusLine label="SYNTHETIC DEMO DATA" alert />
        <p>Decision-support prototype. Not connected to live Indian Railways systems.</p>
      </div>
    </aside>
  );
}

function StatusLine({ label, alert = false }: { label: string; alert?: boolean }) {
  return (
    <div className={`side-status-line ${alert ? 'alert' : ''}`}>
      <span className="status-square" />
      {label}
    </div>
  );
}


