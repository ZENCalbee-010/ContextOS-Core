import { invoke } from "@tauri-apps/api/core";
import type { CommandResult, TokenSavingsReport } from "../types";

const DB_PATH = "data/desktop.db";

type CompressionLevel = "light" | "medium" | "aggressive";

export async function importPath(path: string): Promise<CommandResult> {
  const cleanPath = path.trim();
  if (!cleanPath) {
    return localError(["import"], "Import path is required.");
  }
  return runApprovedCommand(["import", cleanPath]);
}

export async function search(query: string, topK: number): Promise<CommandResult> {
  const cleanQuery = query.trim();
  if (!cleanQuery) {
    return localError(["search"], "Search query is required.");
  }
  return runApprovedCommand([
    "search",
    cleanQuery,
    "--top-k",
    String(clampInteger(topK, 1, 50))
  ]);
}

export async function ask(
  question: string,
  options: { budget: number; dryRun: boolean }
): Promise<CommandResult> {
  const cleanQuestion = question.trim();
  if (!cleanQuestion) {
    return localError(["ask"], "Question is required.");
  }

  const args = [
    "ask",
    cleanQuestion,
    "--adapter",
    "mock",
    "--budget",
    String(Math.max(0, Math.floor(options.budget)))
  ];
  if (options.dryRun) {
    args.push("--dry-run");
  }
  return runApprovedCommand(args);
}

export async function optimize(
  document: string,
  level: CompressionLevel
): Promise<CommandResult> {
  const cleanDocument = document.trim();
  if (!cleanDocument) {
    return localError(["optimize"], "Document id or filepath is required.");
  }
  return runApprovedCommand(["optimize", cleanDocument, "--level", level]);
}

export async function stats(): Promise<CommandResult> {
  return runApprovedCommand(["stats"]);
}

export function parseTokenSavings(output: string): TokenSavingsReport | null {
  const totalAvailable = matchInteger(output, /Total available tokens:\s*(\d+)/i);
  const selectedContext = matchInteger(output, /Selected context tokens:\s*(\d+)/i);
  const saved = matchInteger(output, /Saved tokens:\s*(\d+)/i);
  const savingsPercent = matchFloat(output, /Savings percent:\s*([0-9.]+)%/i);

  if (
    totalAvailable === null ||
    selectedContext === null ||
    saved === null ||
    savingsPercent === null
  ) {
    return null;
  }

  return {
    totalAvailableTokens: totalAvailable,
    selectedContextTokens: selectedContext,
    savedTokens: saved,
    savingsPercent
  };
}

async function runApprovedCommand(args: string[]): Promise<CommandResult> {
  const fullArgs = withDbPath(args);
  const command = formatDisplayCommand(fullArgs);
  const startedAt = performance.now();

  if (!isTauriRuntime()) {
    return {
      status: "idle",
      command,
      args: fullArgs,
      stdout: "",
      stderr: "Desktop command bridge is available when running inside Tauri.",
      exitCode: null,
      durationMs: elapsedMs(startedAt)
    };
  }

  const result = await invoke<CommandResult>("run_context_command", { args: fullArgs });
  return {
    ...result,
    durationMs: result.durationMs ?? elapsedMs(startedAt)
  };
}

function withDbPath(args: string[]): string[] {
  if (args.includes("--db-path")) {
    return args;
  }
  return [...args, "--db-path", DB_PATH];
}

function localError(args: string[], message: string): CommandResult {
  return {
    status: "error",
    command: formatDisplayCommand(args),
    args,
    stdout: "",
    stderr: message,
    exitCode: null,
    durationMs: 0
  };
}

function formatDisplayCommand(args: string[]): string {
  return `python -m contextos.cli.main ${args.map(quoteArg).join(" ")}`;
}

function quoteArg(value: string): string {
  return /\s/.test(value) ? `"${value.replace(/"/g, '\\"')}"` : value;
}

function clampInteger(value: number, min: number, max: number): number {
  if (!Number.isFinite(value)) {
    return min;
  }
  return Math.min(max, Math.max(min, Math.floor(value)));
}

function matchInteger(output: string, pattern: RegExp): number | null {
  const match = output.match(pattern);
  return match ? Number.parseInt(match[1], 10) : null;
}

function matchFloat(output: string, pattern: RegExp): number | null {
  const match = output.match(pattern);
  return match ? Number.parseFloat(match[1]) : null;
}

function isTauriRuntime(): boolean {
  return "__TAURI_INTERNALS__" in window;
}

function elapsedMs(startedAt: number): number {
  return Math.max(0, Math.round(performance.now() - startedAt));
}
