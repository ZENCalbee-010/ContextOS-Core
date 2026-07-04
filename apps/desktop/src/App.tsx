import { useState } from "react";
import { AskPanel } from "./components/AskPanel";
import { CommandLog } from "./components/CommandLog";
import { DocumentList } from "./components/DocumentList";
import { DropZone } from "./components/DropZone";
import { OptimizePanel } from "./components/OptimizePanel";
import { SearchPanel } from "./components/SearchPanel";
import { StatsPanel } from "./components/StatsPanel";
import { TokenSavingsPanel } from "./components/TokenSavingsPanel";
import { parseTokenSavings } from "./api/contextosClient";
import type { CommandLogEntry, CommandResult, TokenSavingsReport } from "./types";

export default function App() {
  const [entries, setEntries] = useState<CommandLogEntry[]>([]);
  const [tokenSavings, setTokenSavings] = useState<TokenSavingsReport | null>(null);
  const latestEntry = entries[0];

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

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">ContextOS Core</p>
          <h1>Desktop Workspace</h1>
          <p className="app-subtitle">
            Import local files, retrieve with BM25, preview prompts safely, and inspect token savings.
          </p>
        </div>
        <div className="runtime-pill">CLI target: python -m contextos.cli.main</div>
      </header>

      <section className="workflow-guide" aria-label="Workflow guide">
        <div>
          <span>1</span>
          <strong>Import</strong>
          <p>Start with files or folders.</p>
        </div>
        <div>
          <span>2</span>
          <strong>Search</strong>
          <p>Check retrieved context.</p>
        </div>
        <div>
          <span>3</span>
          <strong>Ask</strong>
          <p>Use dry-run or mock mode.</p>
        </div>
        <div>
          <span>4</span>
          <strong>Savings</strong>
          <p>See selected versus available tokens.</p>
        </div>
        <div>
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
        <div className="left-column">
          <DropZone onCommandComplete={recordResult} />
          <DocumentList />
          <TokenSavingsPanel report={tokenSavings} />
        </div>

        <div className="main-column">
          <SearchPanel onCommandComplete={recordResult} />
          <AskPanel onCommandComplete={recordResult} />
          <OptimizePanel onCommandComplete={recordResult} />
          <StatsPanel onCommandComplete={recordResult} />
        </div>

        <CommandLog entries={entries} />
      </section>
    </main>
  );
}
