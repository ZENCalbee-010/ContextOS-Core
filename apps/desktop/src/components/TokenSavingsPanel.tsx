import { Panel } from "./Panel";

export function TokenSavingsPanel() {
  return (
    <Panel title="TokenSavingsPanel">
      <div className="metric-grid">
        <div>
          <span>Total available</span>
          <strong>--</strong>
        </div>
        <div>
          <span>Selected</span>
          <strong>--</strong>
        </div>
        <div>
          <span>Saved</span>
          <strong>--</strong>
        </div>
        <div>
          <span>Savings</span>
          <strong>--%</strong>
        </div>
      </div>
    </Panel>
  );
}
