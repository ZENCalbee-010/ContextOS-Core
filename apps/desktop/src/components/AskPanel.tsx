import { useState } from "react";
import { ask as askContext } from "../api/contextosClient";
import type { CommandResult } from "../types";
import { Panel } from "./Panel";

interface AskPanelProps {
  onCommandComplete: (result: CommandResult) => void;
}

export function AskPanel({ onCommandComplete }: AskPanelProps) {
  const [question, setQuestion] = useState("What is ContextOS?");
  const [budget, setBudget] = useState(4000);
  const [dryRun, setDryRun] = useState(true);
  const [isRunning, setIsRunning] = useState(false);

  async function ask() {
    setIsRunning(true);
    try {
      onCommandComplete(await askContext(question, { budget, dryRun }));
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <Panel title="AskPanel">
      <label>
        Question
        <textarea value={question} onChange={(event) => setQuestion(event.target.value)} />
      </label>
      <div className="form-row">
        <label>
          Budget
          <input
            min={0}
            type="number"
            value={budget}
            onChange={(event) => setBudget(Number(event.target.value))}
          />
        </label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={dryRun}
            onChange={(event) => setDryRun(event.target.checked)}
          />
          Dry run
        </label>
      </div>
      <button type="button" onClick={ask} disabled={isRunning || !question.trim()}>
        {isRunning ? "Building context..." : "Ask"}
      </button>
    </Panel>
  );
}
