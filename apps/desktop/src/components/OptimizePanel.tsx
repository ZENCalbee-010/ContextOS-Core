import { useState } from "react";
import { runContextCommand } from "../api/contextosCli";
import type { CommandResult } from "../types";
import { Panel } from "./Panel";

interface OptimizePanelProps {
  onCommandComplete: (result: CommandResult) => void;
}

export function OptimizePanel({ onCommandComplete }: OptimizePanelProps) {
  const [document, setDocument] = useState("1");
  const [level, setLevel] = useState("medium");
  const [isRunning, setIsRunning] = useState(false);

  async function optimize() {
    setIsRunning(true);
    try {
      onCommandComplete(await runContextCommand(["optimize", document, "--level", level]));
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <Panel title="OptimizePanel">
      <div className="form-row">
        <label>
          Document id or filepath
          <input value={document} onChange={(event) => setDocument(event.target.value)} />
        </label>
        <label>
          Level
          <select value={level} onChange={(event) => setLevel(event.target.value)}>
            <option value="light">light</option>
            <option value="medium">medium</option>
            <option value="aggressive">aggressive</option>
          </select>
        </label>
      </div>
      <button type="button" onClick={optimize} disabled={isRunning || !document.trim()}>
        {isRunning ? "Optimizing..." : "Optimize"}
      </button>
    </Panel>
  );
}
