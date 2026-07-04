import type { CommandLogEntry } from "../types";

interface CommandLogProps {
  entries: CommandLogEntry[];
}

export function CommandLog({ entries }: CommandLogProps) {
  async function copyOutput(entry: CommandLogEntry) {
    const output = [entry.stdout, entry.stderr].filter(Boolean).join("\n\n");
    if (!output || !navigator.clipboard) {
      return;
    }
    try {
      await navigator.clipboard.writeText(output);
    } catch {
      return;
    }
  }

  return (
    <aside className="command-log">
      <div className="command-log-heading">
        <h2>CommandLog</h2>
        <span>{entries.length} entries</span>
      </div>
      {entries.length === 0 ? (
        <div className="empty-state">
          <strong>No commands yet</strong>
          <p>Import a folder, search, ask, optimize, or load stats to see command output here.</p>
        </div>
      ) : (
        <div className="log-list">
          {entries.map((entry) => (
            <article key={entry.id} className={`log-entry ${entry.status}`}>
              <div className="log-entry-header">
                <strong>{entry.status === "success" ? "SUCCESS" : entry.status === "error" ? "FAILED" : entry.status.toUpperCase()}</strong>
                <span>{entry.createdAt}</span>
              </div>
              <code>{entry.command}</code>
              <div className="command-meta">
                <span>Exit code: {entry.exitCode ?? "n/a"}</span>
                <span>Duration: {entry.durationMs ?? "n/a"} ms</span>
              </div>
              <button
                type="button"
                className="copy-button"
                onClick={() => void copyOutput(entry)}
                disabled={!entry.stdout && !entry.stderr}
              >
                Copy output
              </button>
              <details className="args-details">
                <summary>Arguments</summary>
                <pre>{JSON.stringify(entry.args, null, 2)}</pre>
              </details>
              {entry.stdout && (
                <details className="stream-details">
                  <summary>stdout</summary>
                  <pre>{entry.stdout}</pre>
                </details>
              )}
              {entry.stderr && (
                <details className="stream-details" open={entry.status === "error"}>
                  <summary>stderr</summary>
                  <pre>{entry.stderr}</pre>
                </details>
              )}
            </article>
          ))}
        </div>
      )}
    </aside>
  );
}
