import type { CommandLogEntry } from "../types";

interface CommandLogProps {
  entries: CommandLogEntry[];
}

export function CommandLog({ entries }: CommandLogProps) {
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
                <strong>{entry.status.toUpperCase()}</strong>
                <span>{entry.createdAt}</span>
              </div>
              <code>{entry.command}</code>
              <div className="command-meta">
                <span>Exit code: {entry.exitCode ?? "n/a"}</span>
                <span>Duration: {entry.durationMs ?? "n/a"} ms</span>
              </div>
              <details className="args-details">
                <summary>Arguments</summary>
                <pre>{JSON.stringify(entry.args, null, 2)}</pre>
              </details>
              {entry.stdout && (
                <>
                  <span className="stream-label">stdout</span>
                  <pre>{entry.stdout}</pre>
                </>
              )}
              {entry.stderr && (
                <>
                  <span className="stream-label">stderr</span>
                  <pre>{entry.stderr}</pre>
                </>
              )}
            </article>
          ))}
        </div>
      )}
    </aside>
  );
}
