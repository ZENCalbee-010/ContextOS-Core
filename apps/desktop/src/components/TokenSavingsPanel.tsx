import type { TokenSavingsReport } from "../types";
import { Panel } from "./Panel";

interface TokenSavingsPanelProps {
  report: TokenSavingsReport | null;
}

export function TokenSavingsPanel({ report }: TokenSavingsPanelProps) {
  const savingsDescription = report
    ? `ContextOS selected ${report.selectedContextTokens} tokens from ${report.totalAvailableTokens} available tokens.`
    : "Run Ask in dry-run or mock mode to calculate token savings.";
  const savingsPercent = report ? Math.max(0, Math.min(100, report.savingsPercent)) : 0;

  return (
    <Panel title="TokenSavingsPanel">
      <p className="panel-copy">{savingsDescription}</p>
      <div className="savings-explainer">
        Token savings compares all imported chunk tokens with the context selected for the current ask flow.
      </div>
      <div className="efficiency-meter">
        <div className="efficiency-meter-header">
          <strong>AI Efficiency</strong>
          <span>{report ? `${savingsPercent.toFixed(2)}% saved` : "Waiting for ask"}</span>
        </div>
        <div className="efficiency-track" aria-label="Token savings efficiency">
          <div style={{ width: `${savingsPercent}%` }} />
        </div>
        <div className="efficiency-flow">
          <span>Original context</span>
          <strong>{report?.totalAvailableTokens ?? "--"}</strong>
          <span>Selected by ContextOS</span>
          <strong>{report?.selectedContextTokens ?? "--"}</strong>
          <span>Tokens avoided</span>
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
          <span>Available tokens</span>
          <strong>{report?.totalAvailableTokens ?? "--"}</strong>
        </div>
        <div>
          <span>Selected tokens</span>
          <strong>{report?.selectedContextTokens ?? "--"}</strong>
        </div>
        <div>
          <span>Tokens saved</span>
          <strong>{report?.savedTokens ?? "--"}</strong>
        </div>
      </div>
    </Panel>
  );
}
