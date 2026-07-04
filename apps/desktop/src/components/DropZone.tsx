import type { DragEvent } from "react";
import { useMemo, useState } from "react";
import { importPath as importContextPath } from "../api/contextosClient";
import type { CommandResult } from "../types";
import { Panel } from "./Panel";

interface DropZoneProps {
  onCommandComplete: (result: CommandResult) => void;
}

interface SelectedImportPath {
  id: string;
  path: string;
  kind: "file" | "folder";
  supported: boolean;
  reason: string;
}

interface DesktopDroppedFile extends File {
  path?: string;
}

const supportedExtensions = new Set([
  ".pdf",
  ".docx",
  ".txt",
  ".md",
  ".markdown",
  ".py",
  ".js",
  ".ts",
  ".tsx",
  ".jsx",
  ".html",
  ".css",
  ".json"
]);

export function DropZone({ onCommandComplete }: DropZoneProps) {
  const [path, setPath] = useState("sample_data");
  const [selectedItems, setSelectedItems] = useState<SelectedImportPath[]>(() => [
    createSelectedPath("sample_data")
  ]);
  const [isDragging, setIsDragging] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const supportedItems = useMemo(
    () => selectedItems.filter((item) => item.supported),
    [selectedItems]
  );

  async function runImport() {
    setIsRunning(true);
    try {
      for (const item of supportedItems) {
        onCommandComplete(await importContextPath(item.path));
      }
    } finally {
      setIsRunning(false);
    }
  }

  function addManualPath() {
    const cleanPath = path.trim();
    if (!cleanPath) {
      return;
    }
    addPaths([cleanPath]);
    setPath("");
  }

  function handleDragOver(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    event.dataTransfer.dropEffect = "copy";
    setIsDragging(true);
  }

  function handleDragLeave() {
    setIsDragging(false);
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);

    const droppedPaths = Array.from(event.dataTransfer.files)
      .map((file) => getDroppedPath(file as DesktopDroppedFile))
      .filter((droppedPath): droppedPath is string => Boolean(droppedPath));

    addPaths(droppedPaths);
  }

  function addPaths(paths: string[]) {
    setSelectedItems((current) => {
      const existing = new Set(current.map((item) => normalizePath(item.path)));
      const nextItems = paths
        .map((itemPath) => createSelectedPath(itemPath))
        .filter((item) => {
          const normalized = normalizePath(item.path);
          if (existing.has(normalized)) {
            return false;
          }
          existing.add(normalized);
          return true;
        });
      return [...current, ...nextItems];
    });
  }

  function removePath(id: string) {
    setSelectedItems((current) => current.filter((item) => item.id !== id));
  }

  function clearPaths() {
    setSelectedItems([]);
  }

  return (
    <Panel title="DropZone">
      <div
        className={isDragging ? "drop-zone dragging" : "drop-zone"}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <span>Start here: import local context</span>
        <small>Drag files or folders here, or add a path manually below.</small>
      </div>
      <label>
        File or folder path
        <input value={path} onChange={(event) => setPath(event.target.value)} />
      </label>
      <div className="drop-zone-actions">
        <button type="button" className="secondary-button" onClick={addManualPath} disabled={!path.trim()}>
          Add Path
        </button>
        <button type="button" className="secondary-button" onClick={clearPaths} disabled={selectedItems.length === 0}>
          Clear
        </button>
        <button type="button" onClick={runImport} disabled={isRunning || supportedItems.length === 0}>
          {isRunning ? "Importing..." : `Import ${supportedItems.length || ""}`.trim()}
        </button>
      </div>

      <div className="selection-summary">
        <strong>{selectedItems.length} selected</strong>
        <span>{supportedItems.length} supported</span>
        <span>{selectedItems.length - supportedItems.length} unsupported</span>
      </div>

      {selectedItems.length === 0 ? (
        <div className="empty-state">
          <strong>No files selected</strong>
          <p>Drop PDF, DOCX, TXT, Markdown, source code files, or folders to prepare an import.</p>
        </div>
      ) : (
        <div className="selected-path-list">
          {selectedItems.map((item) => (
            <article key={item.id} className={item.supported ? "selected-path supported" : "selected-path unsupported"}>
              <div>
                <strong>{item.path}</strong>
                <span>{item.kind} · {item.reason}</span>
              </div>
              <button type="button" className="icon-button" onClick={() => removePath(item.id)} aria-label={`Remove ${item.path}`}>
                Remove
              </button>
            </article>
          ))}
        </div>
      )}
    </Panel>
  );
}

function createSelectedPath(path: string): SelectedImportPath {
  const cleanPath = path.trim();
  const kind = inferKind(cleanPath);
  const extension = getExtension(cleanPath);
  const supported = kind === "folder" || supportedExtensions.has(extension);

  return {
    id: `${cleanPath}-${Date.now()}-${Math.random().toString(16).slice(2)}`,
    path: cleanPath,
    kind,
    supported,
    reason: supported
      ? kind === "folder"
        ? "folder import"
        : `${extension} supported`
      : extension
        ? `${extension} is not supported`
        : "unsupported file type"
  };
}

function getDroppedPath(file: DesktopDroppedFile): string | null {
  return file.path || file.webkitRelativePath || file.name || null;
}

function inferKind(path: string): "file" | "folder" {
  const normalized = path.replace(/\\/g, "/");
  const name = normalized.split("/").filter(Boolean).pop() ?? normalized;
  return name.includes(".") ? "file" : "folder";
}

function getExtension(path: string): string {
  const normalized = path.replace(/\\/g, "/");
  const name = normalized.split("/").filter(Boolean).pop() ?? normalized;
  const index = name.lastIndexOf(".");
  return index >= 0 ? name.slice(index).toLowerCase() : "";
}

function normalizePath(path: string): string {
  return path.trim().replace(/\\/g, "/").toLowerCase();
}
