import { Panel } from "./Panel";

export function DocumentList() {
  return (
    <Panel title="DocumentList">
      <div className="placeholder-list">
        <div>
          <strong>No document browser yet</strong>
          <span>Imported files are stored in data/desktop.db. Use Stats after import to confirm totals.</span>
        </div>
        <div>
          <strong>Next milestone</strong>
          <span>This panel will list document paths, chunk counts, and source metadata.</span>
        </div>
      </div>
    </Panel>
  );
}
