import { useState } from "react";
import { importPath as importContextPath } from "../api/contextosClient";
import type { CommandResult } from "../types";
import { Panel } from "./Panel";

interface DropZoneProps {
  onCommandComplete: (result: CommandResult) => void;
}

export function DropZone({ onCommandComplete }: DropZoneProps) {
  const [path, setPath] = useState("sample_data");
  const [isRunning, setIsRunning] = useState(false);

  async function runImport() {
    setIsRunning(true);
    try {
      onCommandComplete(await importContextPath(path));
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <Panel title="DropZone">
      <div className="drop-zone">
        <span>Drop files here</span>
        <small>Phase 2 scaffold uses a path field until native drag/drop is wired.</small>
      </div>
      <label>
        Import path
        <input value={path} onChange={(event) => setPath(event.target.value)} />
      </label>
      <button type="button" onClick={runImport} disabled={isRunning || !path.trim()}>
        {isRunning ? "Importing..." : "Import"}
      </button>
    </Panel>
  );
}
