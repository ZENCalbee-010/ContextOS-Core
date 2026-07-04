import { useState } from "react";
import { benchmark } from "../api/contextosClient";
import type { CommandResult } from "../types";
import { Panel } from "./Panel";

interface BenchmarkPanelProps {
  onCommandComplete: (result: CommandResult) => void;
}

interface BenchmarkMetric {
  label: string;
  value: string;
}

export function BenchmarkPanel({ onCommandComplete }: BenchmarkPanelProps) {
  const [query, setQuery] = useState("context selection");
  const [question, setQuestion] = useState("How does ContextOS save tokens?");
  const [iterations, setIterations] = useState(3);
  const [isRunning, setIsRunning] = useState(false);
  const [lastResult, setLastResult] = useState<CommandResult | null>(null);
  const [validationMessage, setValidationMessage] = useState<string | null>(null);

  async function runBenchmark() {
    if (!query.trim()) {
      setValidationMessage("Benchmark query is required.");
      return;
    }
    if (!question.trim()) {
      setValidationMessage("Benchmark question is required.");
      return;
    }
    if (!Number.isFinite(iterations) || iterations < 1) {
      setValidationMessage("Iterations must be at least 1.");
      return;
    }

    setIsRunning(true);
    setValidationMessage(null);
    try {
      const result = await benchmark({ query, question, iterations });
      setLastResult(result);
      onCommandComplete(result);
    } finally {
      setIsRunning(false);
    }
  }

  const metrics = lastResult ? parseBenchmarkMetrics(lastResult.stdout) : [];
  const reportPath = lastResult?.stdout.match(/Report:\s*(.+)/i)?.[1]?.trim() ?? "benchmark_report_desktop.md";

  return (
    <Panel title="BenchmarkPanel">
      <p className="panel-copy">Run the local benchmark over the sample dataset without calling a real AI adapter.</p>
      <div className="form-row">
        <label>
          Query
          <input value={query} onChange={(event) => setQuery(event.target.value)} />
        </label>
        <label>
          Iterations
          <input
            min={1}
            type="number"
            value={iterations}
            onChange={(event) => setIterations(Number(event.target.value))}
          />
        </label>
      </div>
      <label>
        Question
        <input value={question} onChange={(event) => setQuestion(event.target.value)} />
      </label>
      <div className="output-path">
        <span>Output</span>
        <strong>{reportPath}</strong>
      </div>
      {validationMessage && <div className="inline-error">{validationMessage}</div>}
      <button type="button" onClick={runBenchmark} disabled={isRunning}>
        {isRunning ? "Running benchmark..." : "Run Benchmark"}
      </button>

      <section className="benchmark-results" aria-live="polite">
        {!lastResult && (
          <div className="empty-state">
            <strong>No benchmark yet</strong>
            <p>Run the benchmark to measure import, search, ask dry-run, compression, and token savings.</p>
          </div>
        )}

        {lastResult?.status === "idle" && (
          <div className="empty-state">
            <strong>Desktop bridge unavailable</strong>
            <p>Run inside the Tauri desktop shell to execute the real benchmark command.</p>
          </div>
        )}

        {lastResult?.status === "error" && (
          <div className="inline-error">
            {lastResult.stderr || "Benchmark command failed. Check the dataset path and iterations."}
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

function parseBenchmarkMetrics(output: string): BenchmarkMetric[] {
  const metricLabels = [
    "Import latency",
    "Search latency",
    "Ask dry-run latency",
    "Total tokens",
    "Selected context tokens",
    "Saved tokens",
    "Savings percent",
    "Compression ratio"
  ];

  return metricLabels
    .map((label) => {
      const value = output.match(new RegExp(`${label}:\\s*(.+)`, "i"))?.[1]?.trim();
      return value ? { label, value } : null;
    })
    .filter((metric): metric is BenchmarkMetric => metric !== null);
}
