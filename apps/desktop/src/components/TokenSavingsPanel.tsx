import type { TokenSavingsReport } from "../types";
import { Panel } from "./Panel";

interface TokenSavingsPanelProps {
  report: TokenSavingsReport | null;
}

export function TokenSavingsPanel({ report }: TokenSavingsPanelProps) {
  const savingsDescription = report
    ? `${report.savedTokens} tokens avoided from the currently imported context.`
    : "Run Ask to populate the latest token savings report.";

  return (
    <Panel title="TokenSavingsPanel">
      <p className="panel-copy">{savingsDescription}</p>
      <div className="metric-grid">
        <div className="primary-metric">
          <span>Savings</span>
          <strong>
            {report ? `${report.savingsPercent.toFixed(2)}%` : "--%"}
          </strong>
        </div>
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
      </div>
    </Panel>
  );
}
