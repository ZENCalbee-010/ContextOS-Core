import { useState } from "react";
import { AskPanel } from "./components/AskPanel";
import { CommandLog } from "./components/CommandLog";
import { DocumentList } from "./components/DocumentList";
import { DropZone } from "./components/DropZone";
import { OptimizePanel } from "./components/OptimizePanel";
import { SearchPanel } from "./components/SearchPanel";
import { StatsPanel } from "./components/StatsPanel";
import { TokenSavingsPanel } from "./components/TokenSavingsPanel";
import type { CommandLogEntry, CommandResult } from "./types";

export default function App() {
  const [entries, setEntries] = useState<CommandLogEntry[]>([]);

  function recordResult(result: CommandResult) {
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
          <TokenSavingsPanel />
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
