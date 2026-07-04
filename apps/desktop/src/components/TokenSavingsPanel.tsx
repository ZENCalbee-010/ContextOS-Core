import type { TokenSavingsReport } from "../types";
import { Panel } from "./Panel";

interface TokenSavingsPanelProps {
  report: TokenSavingsReport | null;
}

export function TokenSavingsPanel({ report }: TokenSavingsPanelProps) {
  const savingsDescription = report
    ? `${report.savedTokens} tokens avoided from the currently imported context.`
    : "Run Ask to populate the latest token savings report.";
  const savingsPercent = report ? Math.max(0, Math.min(100, report.savingsPercent)) : 0;

  return (
    <Panel title="TokenSavingsPanel">
      <p className="panel-copy">{savingsDescription}</p>
      <div className="efficiency-meter">
        <div className="efficiency-meter-header">
          <strong>AI Efficiency</strong>
          <span>{report ? `${savingsPercent.toFixed(2)}% saved` : "Waiting for ask"}</span>
        </div>
        <div className="efficiency-track" aria-label="Token savings efficiency">
          <div style={{ width: `${savingsPercent}%` }} />
        </div>
        <div className="efficiency-flow">
          <span>Original</span>
          <strong>{report?.totalAvailableTokens ?? "--"}</strong>
          <span>ContextOS</span>
          <strong>{report?.selectedContextTokens ?? "--"}</strong>
          <span>Saved</span>
          <strong>{report?.savedTokens ?? "--"}</strong>
        </div>
      </div>
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
