import { Panel } from "./Panel";

export function DocumentList() {
  return (
    <Panel title="DocumentList">
      <div className="placeholder-list">
        <div>
          <strong>Imported documents</strong>
          <span>Placeholder for indexed files from data/desktop.db</span>
        </div>
        <div>
          <strong>Recent chunks</strong>
          <span>Placeholder for source previews and metadata</span>
        </div>
      </div>
    </Panel>
  );
}
