import { useState } from "react";
import { ask as askContext } from "../api/contextosClient";
import type { CommandResult } from "../types";
import { Panel } from "./Panel";

interface AskPanelProps {
  onCommandComplete: (result: CommandResult) => void;
}

type AskMode = "dry-run" | "mock";

export function AskPanel({ onCommandComplete }: AskPanelProps) {
  const [question, setQuestion] = useState("What is ContextOS?");
  const [budget, setBudget] = useState(4000);
  const [topK, setTopK] = useState(10);
  const [mode, setMode] = useState<AskMode>("dry-run");
  const [isRunning, setIsRunning] = useState(false);
  const [lastResult, setLastResult] = useState<CommandResult | null>(null);
  const [lastQuestion, setLastQuestion] = useState<string | null>(null);
  const [validationMessage, setValidationMessage] = useState<string | null>(null);

  async function ask() {
    const cleanQuestion = question.trim();
    if (!cleanQuestion) {
      setValidationMessage("Enter a question after importing files.");
      return;
    }

    setIsRunning(true);
    setValidationMessage(null);
    try {
      const result = await askContext(cleanQuestion, { budget, mode, topK });
      setLastQuestion(cleanQuestion);
      setLastResult(result);
      onCommandComplete(result);
    } finally {
      setIsRunning(false);
    }
  }

  const promptPreview = lastResult ? extractPromptPreview(lastResult.stdout) : "";
  const mockAnswer = lastResult ? extractMockAnswer(lastResult.stdout) : "";
  const sources = lastResult ? extractSources(lastResult.stdout) : [];
  const hasRawOutput = Boolean(lastResult?.stdout || lastResult?.stderr);
  const resultTitle = mode === "dry-run" ? "Prompt Preview" : "Mock Answer";

  return (
    <Panel title="AskPanel">
      <p className="panel-copy">Dry-run shows the selected prompt without an AI call. Mock mode stays local.</p>
      <label>
        Question
        <textarea value={question} onChange={(event) => setQuestion(event.target.value)} />
      </label>
      <div className="form-row">
        <label>
          Mode
          <select value={mode} onChange={(event) => setMode(event.target.value as AskMode)}>
            <option value="dry-run">Dry run</option>
            <option value="mock">Mock</option>
          </select>
        </label>
        <label>
          Budget
          <input
            min={0}
            type="number"
            value={budget}
            onChange={(event) => setBudget(Number(event.target.value))}
          />
        </label>
      </div>
      <div className="form-row">
        <label>
          Top K
          <input
            min={1}
            max={50}
            type="number"
            value={topK}
            onChange={(event) => setTopK(Number(event.target.value))}
          />
        </label>
        <div className="mode-note">
          {mode === "dry-run" ? "No AI call. Shows selected prompt." : "Uses local mock adapter only."}
        </div>
      </div>
      {validationMessage && <div className="inline-error">{validationMessage}</div>}
      <button type="button" onClick={ask} disabled={isRunning || !question.trim()}>
        {isRunning ? "Building context..." : "Ask"}
      </button>

      <section className="ask-results" aria-live="polite">
        <div className="result-summary">
          <strong>{lastQuestion ? `Last question: ${lastQuestion}` : resultTitle}</strong>
          <span>{isRunning ? "Running..." : lastResult ? lastResult.status : "Ready"}</span>
        </div>

        {!lastResult && (
          <div className="empty-state">
            <strong>No question submitted</strong>
            <p>Import files first, then ask with dry-run or mock mode to inspect selected context.</p>
          </div>
        )}

        {lastResult?.status === "idle" && (
          <div className="empty-state">
            <strong>Desktop bridge unavailable</strong>
            <p>Run inside the Tauri desktop shell to execute the real ask command.</p>
          </div>
        )}

        {lastResult?.status === "error" && (
          <div className="inline-error">
            {lastResult.stderr || "Ask command failed. Import files first, then ask again."}
          </div>
        )}

        {promptPreview && (
          <div className="prompt-preview">
            <strong>Prompt Preview</strong>
            <pre>{promptPreview}</pre>
          </div>
        )}

        {mockAnswer && (
          <div className="prompt-preview">
            <strong>Mock Answer</strong>
            <pre>{mockAnswer}</pre>
          </div>
        )}

        {sources.length > 0 && (
          <div className="source-list">
            <strong>Sources</strong>
            {sources.map((source) => (
              <span key={source}>{source}</span>
            ))}
          </div>
        )}

        {!promptPreview && !mockAnswer && lastResult && hasRawOutput && (
          <div className="raw-output">
            <strong>Raw output</strong>
            {lastResult.stdout && <pre>{lastResult.stdout}</pre>}
            {lastResult.stderr && <pre>{lastResult.stderr}</pre>}
          </div>
        )}
      </section>
    </Panel>
  );
}

function extractPromptPreview(output: string): string {
  const systemIndex = output.indexOf("SYSTEM:");
  if (systemIndex >= 0) {
    return output.slice(systemIndex).trim();
  }
  return "";
}

function extractMockAnswer(output: string): string {
  const tokenSavingsIndex = output.indexOf("TOKEN SAVINGS REPORT");
  const answerSection = tokenSavingsIndex >= 0 ? output.slice(0, tokenSavingsIndex) : output;
  const cleaned = answerSection.trim();

  if (!cleaned || extractPromptPreview(output)) {
    return "";
  }
  return cleaned;
}

function extractSources(output: string): string[] {
  const sourceMatches = Array.from(output.matchAll(/^Source:\s*(.+)$/gim)).map((match) => match[1].trim());
  const sourcesSection = output.match(/Sources:\s*([\s\S]+)/i)?.[1] ?? "";
  const listedSources = sourcesSection
    .split(/\r?\n/)
    .map((line) => line.replace(/^[-*]\s*/, "").trim())
    .filter((line) => line.length > 0);

  return Array.from(new Set([...sourceMatches, ...listedSources])).slice(0, 8);
}
