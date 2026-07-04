import type { CommandLogEntry } from "../types";

interface CommandLogProps {
  entries: CommandLogEntry[];
}

export function CommandLog({ entries }: CommandLogProps) {
  return (
    <aside className="command-log">
      <h2>CommandLog</h2>
      {entries.length === 0 ? (
        <p className="empty-state">Commands will appear here.</p>
      ) : (
        <div className="log-list">
          {entries.map((entry) => (
            <article key={entry.id} className={`log-entry ${entry.status}`}>
              <div className="log-entry-header">
                <strong>{entry.status}</strong>
                <span>{entry.createdAt}</span>
              </div>
              <code>{entry.command}</code>
              <div className="exit-code">Exit code: {entry.exitCode ?? "n/a"}</div>
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
