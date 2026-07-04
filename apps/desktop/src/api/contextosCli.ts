import { invoke } from "@tauri-apps/api/core";
import type { CommandResult } from "../types";

const DB_PATH = "data/desktop.db";

export async function runContextCommand(args: string[]): Promise<CommandResult> {
  const fullArgs = withDbPath(args);
  const command = `python -m contextos.cli.main ${fullArgs.join(" ")}`;

  if (!isTauriRuntime()) {
    return {
      status: "idle",
      command,
      output: "Desktop command bridge is available when running inside Tauri."
    };
  }

  return invoke<CommandResult>("run_context_command", { args: fullArgs });
}

function withDbPath(args: string[]): string[] {
  if (args.includes("--db-path")) {
    return args;
  }
  return [...args, "--db-path", DB_PATH];
}

function isTauriRuntime(): boolean {
  return "__TAURI_INTERNALS__" in window;
}
