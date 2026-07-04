interface AppHeaderProps {
  activeView: string;
  theme: "light" | "dark";
  onToggleTheme: () => void;
}

const viewTitles: Record<string, { title: string; description: string }> = {
  import: {
    title: "Import Workspace",
    description: "Bring local files into ContextOS before searching or asking."
  },
  search: {
    title: "Search Context",
    description: "Inspect BM25 retrieval results from the local SQLite workspace."
  },
  ask: {
    title: "Ask Safely",
    description: "Preview selected context with dry-run or use the local mock adapter."
  },
  savings: {
    title: "Token Savings",
    description: "Compare the full imported context with the selected prompt context."
  },
  benchmark: {
    title: "Benchmark",
    description: "Review local performance and efficiency signals from ContextOS."
  },
  stats: {
    title: "Workspace Stats",
    description: "Check document, chunk, compression, and query totals."
  },
  settings: {
    title: "Settings",
    description: "Review local runtime paths and desktop preferences."
  }
};

export function AppHeader({ activeView, theme, onToggleTheme }: AppHeaderProps) {
  const copy = viewTitles[activeView] ?? viewTitles.import;

  return (
    <header className="app-header">
      <div>
        <p className="eyebrow">ContextOS Desktop</p>
        <h1>{copy.title}</h1>
        <p className="app-subtitle">{copy.description}</p>
      </div>
      <div className="header-actions">
        <div className="runtime-pill">python -m contextos.cli.main</div>
        <button type="button" className="secondary-button" onClick={onToggleTheme}>
          {theme === "dark" ? "Light" : "Dark"}
        </button>
      </div>
    </header>
  );
}
