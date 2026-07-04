import type { TokenSavingsReport } from "../types";
import { Panel } from "./Panel";

interface TokenSavingsPanelProps {
  report: TokenSavingsReport | null;
}

export function TokenSavingsPanel({ report }: TokenSavingsPanelProps) {
  return (
    <Panel title="TokenSavingsPanel">
      <div className="metric-grid">
        <div>
          <span>Total available</span>
          <strong>{report?.totalAvailableTokens ?? "--"}</strong>
        </div>
        <div>
          <span>Selected</span>
          <strong>{report?.selectedContextTokens ?? "--"}</strong>
        </div>
        <div>
          <span>Saved</span>
          <strong>{report?.savedTokens ?? "--"}</strong>
        </div>
        <div>
          <span>Savings</span>
          <strong>
            {report ? `${report.savingsPercent.toFixed(2)}%` : "--%"}
          </strong>
        </div>
      </div>
    </Panel>
  );
}
