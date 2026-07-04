import { useState } from "react";
import { stats } from "../api/contextosClient";
import type { CommandResult } from "../types";
import { Panel } from "./Panel";

interface StatsPanelProps {
  onCommandComplete: (result: CommandResult) => void;
}

interface StatsMetric {
  label: string;
  value: string;
}

export function StatsPanel({ onCommandComplete }: StatsPanelProps) {
  const [isRunning, setIsRunning] = useState(false);
  const [lastResult, setLastResult] = useState<CommandResult | null>(null);

  async function loadStats() {
    setIsRunning(true);
    try {
      const result = await stats();
      setLastResult(result);
      onCommandComplete(result);
    } finally {
      setIsRunning(false);
    }
  }

  const metrics = lastResult ? parseStatsMetrics(lastResult.stdout) : [];

  return (
    <Panel title="StatsPanel">
      <p className="panel-copy">Load workspace totals, compression metrics, latency, and latest token savings.</p>
      <button type="button" onClick={loadStats} disabled={isRunning}>
        {isRunning ? "Refreshing..." : "Refresh Stats"}
      </button>

      <section className="stats-results" aria-live="polite">
        {!lastResult && (
          <div className="empty-state">
            <strong>No stats loaded</strong>
            <p>Import files first, then refresh stats to inspect the local SQLite workspace.</p>
          </div>
        )}

        {lastResult?.status === "idle" && (
          <div className="empty-state">
            <strong>Desktop bridge unavailable</strong>
            <p>Run inside the Tauri desktop shell to execute the real stats command.</p>
          </div>
        )}

        {lastResult?.status === "error" && (
          <div className="inline-error">
            {lastResult.stderr || "Stats command failed. Import files first, then refresh stats."}
          </div>
        )}

        {metrics.length > 0 ? (
          <div className="metric-grid">
            {metrics.map((metric) => (
              <div key={metric.label}>
                <span>{metric.label}</span>
                <strong>{metric.value}</strong>
              </div>
            ))}
          </div>
        ) : (
          lastResult && (lastResult.stdout || lastResult.stderr) && (
            <div className="raw-output">
              <strong>Raw output</strong>
              {lastResult.stdout && <pre>{lastResult.stdout}</pre>}
              {lastResult.stderr && <pre>{lastResult.stderr}</pre>}
            </div>
          )
        )}
      </section>
    </Panel>
  );
}

function parseStatsMetrics(output: string): StatsMetric[] {
  return output
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const [label, ...valueParts] = line.split(":");
      const value = valueParts.join(":").trim();
      return label && value ? { label, value } : null;
    })
    .filter((metric): metric is StatsMetric => metric !== null);
}
