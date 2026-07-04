import { useState } from "react";
import { search as searchContext } from "../api/contextosClient";
import type { CommandResult } from "../types";
import { Panel } from "./Panel";

interface SearchPanelProps {
  onCommandComplete: (result: CommandResult) => void;
}

interface SearchResultPreview {
  index: number;
  score: string;
  source: string;
  preview: string;
}

export function SearchPanel({ onCommandComplete }: SearchPanelProps) {
  const [query, setQuery] = useState("context selection");
  const [topK, setTopK] = useState(5);
  const [isRunning, setIsRunning] = useState(false);
  const [lastQuery, setLastQuery] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<CommandResult | null>(null);
  const [validationMessage, setValidationMessage] = useState<string | null>(null);

  async function search() {
    const cleanQuery = query.trim();
    if (!cleanQuery) {
      setValidationMessage("Enter a search query after importing files.");
      return;
    }

    setIsRunning(true);
    setValidationMessage(null);
    try {
      const result = await searchContext(cleanQuery, topK);
      setLastQuery(cleanQuery);
      setLastResult(result);
      onCommandComplete(result);
    } finally {
      setIsRunning(false);
    }
  }

  const parsedResults = lastResult ? parseSearchResults(lastResult.stdout) : [];
  const hasRawOutput = Boolean(lastResult?.stdout || lastResult?.stderr);
  const resultCount = parsedResults.length || parseResultCount(lastResult?.stdout ?? "");
  const emptyStateMessage = lastResult
    ? "No structured search results were detected. Raw command output is shown below."
    : "Import files first, then search your context.";

  return (
    <Panel title="SearchPanel">
      <p className="panel-copy">Search imported chunks before asking so you can inspect what BM25 retrieves.</p>
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
      {validationMessage && <div className="inline-error">{validationMessage}</div>}
      <button type="button" onClick={search} disabled={isRunning || !query.trim()}>
        {isRunning ? "Searching..." : "Search"}
      </button>

      <section className="search-results" aria-live="polite">
        <div className="result-summary">
          <strong>{lastQuery ? `Last search: ${lastQuery}` : "Search results"}</strong>
          <span>{isRunning ? "Running..." : `${resultCount} result${resultCount === 1 ? "" : "s"}`}</span>
        </div>

        {!lastResult && (
          <div className="empty-state">
            <strong>No search yet</strong>
            <p>{emptyStateMessage}</p>
          </div>
        )}

        {lastResult?.status === "idle" && (
          <div className="empty-state">
            <strong>Desktop bridge unavailable</strong>
            <p>Run inside the Tauri desktop shell to execute the real search command.</p>
          </div>
        )}

        {lastResult?.status === "error" && (
          <div className="inline-error">
            {lastResult.stderr || "Search command failed. Import files first, then search your context."}
          </div>
        )}

        {parsedResults.length > 0 ? (
          <div className="result-list">
            {parsedResults.map((result) => (
              <article key={result.index} className="search-result-card">
                <div className="search-result-heading">
                  <strong>Result {result.index}</strong>
                  <span>Score {result.score}</span>
                </div>
                <p>{result.source}</p>
                <div>{result.preview}</div>
              </article>
            ))}
          </div>
        ) : (
          lastResult && hasRawOutput && (
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

function parseResultCount(output: string): number {
  return output.match(/\[Result\s+\d+\]/g)?.length ?? 0;
}

function parseSearchResults(output: string): SearchResultPreview[] {
  return output
    .split(/\n\s*\n/)
    .map((block) => block.trim())
    .filter(Boolean)
    .map((block) => {
      const index = block.match(/\[Result\s+(\d+)\]/i)?.[1];
      const score = block.match(/Score:\s*(.+)/i)?.[1];
      const source = block.match(/Source:\s*(.+)/i)?.[1];
      const preview = block.match(/Preview:\s*([\s\S]+)/i)?.[1];

      if (!index || !score || !source || !preview) {
        return null;
      }

      return {
        index: Number.parseInt(index, 10),
        score: score.trim(),
        source: source.trim(),
        preview: preview.trim()
      };
    })
    .filter((result): result is SearchResultPreview => result !== null);
}
