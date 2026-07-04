import { useState } from "react";
import { stats } from "../api/contextosClient";
import type { CommandResult } from "../types";
import { Panel } from "./Panel";

interface StatsPanelProps {
  onCommandComplete: (result: CommandResult) => void;
}

export function StatsPanel({ onCommandComplete }: StatsPanelProps) {
  const [isRunning, setIsRunning] = useState(false);

  async function loadStats() {
    setIsRunning(true);
    try {
      onCommandComplete(await stats());
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <Panel title="StatsPanel">
      <p className="panel-copy">Load workspace totals, compression metrics, latency, and latest token savings.</p>
      <button type="button" onClick={loadStats} disabled={isRunning}>
        {isRunning ? "Loading..." : "Load Stats"}
      </button>
    </Panel>
  );
}
