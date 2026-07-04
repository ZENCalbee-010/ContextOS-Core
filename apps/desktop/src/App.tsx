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
        </div>
        <div className="runtime-pill">CLI target: python -m contextos.cli.main</div>
      </header>

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
