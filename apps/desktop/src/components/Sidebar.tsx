interface SidebarProps {
  activeView: string;
  onSelectView: (view: string) => void;
}

const navItems = [
  { id: "import", label: "Import", meta: "Files and folders" },
  { id: "search", label: "Search", meta: "BM25 results" },
  { id: "ask", label: "Ask", meta: "Dry-run / mock" },
  { id: "savings", label: "Savings", meta: "Token dashboard" },
  { id: "benchmark", label: "Benchmark", meta: "Latency report" },
  { id: "stats", label: "Stats", meta: "Workspace totals" },
  { id: "settings", label: "Settings", meta: "Local runtime" }
];

export function Sidebar({ activeView, onSelectView }: SidebarProps) {
  return (
    <aside className="sidebar" aria-label="Primary navigation">
      <div className="brand-lockup">
        <div className="brand-mark">C</div>
        <div>
          <strong>ContextOS</strong>
          <span>Level 2 Desktop</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <button
            key={item.id}
            type="button"
            className={activeView === item.id ? "nav-item active" : "nav-item"}
            onClick={() => onSelectView(item.id)}
          >
            <span>{item.label}</span>
            <small>{item.meta}</small>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <span>Local-first</span>
        <strong>SQLite + BM25</strong>
      </div>
    </aside>
  );
}
