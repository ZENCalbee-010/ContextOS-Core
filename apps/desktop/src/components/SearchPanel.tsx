import { useState } from "react";
import { runContextCommand } from "../api/contextosCli";
import type { CommandResult } from "../types";
import { Panel } from "./Panel";

interface SearchPanelProps {
  onCommandComplete: (result: CommandResult) => void;
}

export function SearchPanel({ onCommandComplete }: SearchPanelProps) {
  const [query, setQuery] = useState("context selection");
  const [topK, setTopK] = useState(5);
  const [isRunning, setIsRunning] = useState(false);

  async function search() {
    setIsRunning(true);
    try {
      onCommandComplete(
        await runContextCommand(["search", query, "--top-k", String(topK)])
      );
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <Panel title="SearchPanel">
      <div className="form-row">
        <label>
          Query
          <input value={query} onChange={(event) => setQuery(event.target.value)} />
        </label>
        <label>
          Top K
          <input
            min={1}
            max={20}
            type="number"
            value={topK}
            onChange={(event) => setTopK(Number(event.target.value))}
          />
        </label>
      </div>
      <button type="button" onClick={search} disabled={isRunning || !query.trim()}>
        {isRunning ? "Searching..." : "Search"}
      </button>
    </Panel>
  );
}
