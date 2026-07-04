import { useEffect, useState } from "react";
import { AppHeader } from "./components/AppHeader";
import { AskPanel } from "./components/AskPanel";
import { CommandLog } from "./components/CommandLog";
import { DocumentList } from "./components/DocumentList";
import { DropZone } from "./components/DropZone";
import { OptimizePanel } from "./components/OptimizePanel";
import { SearchPanel } from "./components/SearchPanel";
import { SettingsPanel } from "./components/SettingsPanel";
import { Sidebar } from "./components/Sidebar";
import { StatsPanel } from "./components/StatsPanel";
import { TokenSavingsPanel } from "./components/TokenSavingsPanel";
import { parseTokenSavings } from "./api/contextosClient";
import type { CommandLogEntry, CommandResult, TokenSavingsReport } from "./types";

export default function App() {
  const [entries, setEntries] = useState<CommandLogEntry[]>([]);
  const [tokenSavings, setTokenSavings] = useState<TokenSavingsReport | null>(null);
  const [activeView, setActiveView] = useState("import");
  const [theme, setTheme] = useState<"light" | "dark">(() => {
    const savedTheme = window.localStorage.getItem("contextos-theme");
    return savedTheme === "dark" ? "dark" : "light";
  });
  const latestEntry = entries[0];

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem("contextos-theme", theme);
  }, [theme]);

  function recordResult(result: CommandResult) {
    const parsedSavings = parseTokenSavings(`${result.stdout}\n${result.stderr}`);
    if (parsedSavings) {
      setTokenSavings(parsedSavings);
    }

    setEntries((current) => [
      {
        ...result,
        id: Date.now(),
        createdAt: new Date().toLocaleTimeString()
      },
      ...current
    ]);
  }

  function renderWorkspace() {
    if (activeView === "import") {
      return (
        <>
          <DropZone onCommandComplete={recordResult} />
          <DocumentList />
        </>
      );
    }

    if (activeView === "search") {
      return <SearchPanel onCommandComplete={recordResult} />;
    }

    if (activeView === "ask") {
      return (
        <>
          <AskPanel onCommandComplete={recordResult} />
          <TokenSavingsPanel report={tokenSavings} />
        </>
      );
    }

    if (activeView === "savings") {
      return <TokenSavingsPanel report={tokenSavings} />;
    }

    if (activeView === "benchmark") {
      return (
        <section className="panel benchmark-placeholder">
          <h2>Benchmark</h2>
          <p className="panel-copy">
            Run the benchmark command from the CLI today, then review the generated Markdown report.
          </p>
          <code>
            python -m contextos.cli.main benchmark --dataset sample_data/benchmark --db-path
            data/benchmark.db
          </code>
        </section>
      );
    }

    if (activeView === "stats") {
      return (
        <>
          <StatsPanel onCommandComplete={recordResult} />
          <OptimizePanel onCommandComplete={recordResult} />
        </>
      );
    }

    return <SettingsPanel theme={theme} onThemeChange={setTheme} />;
  }

  return (
    <main className="app-shell">
      <Sidebar activeView={activeView} onSelectView={setActiveView} />
      <section className="desktop-surface">
        <AppHeader
          activeView={activeView}
          theme={theme}
          onToggleTheme={() => setTheme((current) => (current === "dark" ? "light" : "dark"))}
        />

        <section className="workflow-guide" aria-label="Workflow guide">
          <div className={activeView === "import" ? "current" : ""}>
            <span>1</span>
            <strong>Import</strong>
            <p>Start with files or folders.</p>
          </div>
          <div className={activeView === "search" ? "current" : ""}>
            <span>2</span>
            <strong>Search</strong>
            <p>Check retrieved context.</p>
          </div>
          <div className={activeView === "ask" ? "current" : ""}>
            <span>3</span>
            <strong>Ask</strong>
            <p>Use dry-run or mock mode.</p>
          </div>
          <div className={activeView === "savings" ? "current" : ""}>
            <span>4</span>
            <strong>Savings</strong>
            <p>See selected versus available tokens.</p>
          </div>
          <div className={activeView === "stats" ? "current" : ""}>
            <span>5</span>
            <strong>Stats</strong>
            <p>Review workspace totals.</p>
          </div>
        </section>

        {latestEntry && (
          <section className={`status-banner ${latestEntry.status}`} aria-live="polite">
            <strong>{latestEntry.status === "success" ? "Command completed" : "Latest command"}</strong>
            <span>{latestEntry.command}</span>
          </section>
        )}

        <section className="workspace-grid">
          <div className="main-column">{renderWorkspace()}</div>
          <CommandLog entries={entries} />
        </section>
      </section>
    </main>
  );
}
