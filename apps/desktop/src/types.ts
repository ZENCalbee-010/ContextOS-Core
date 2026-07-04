export type CommandStatus = "idle" | "running" | "success" | "error";

export interface CommandResult {
  status: CommandStatus;
  command: string;
  args: string[];
  stdout: string;
  stderr: string;
  exitCode: number | null;
  durationMs: number | null;
}

export interface CommandLogEntry extends CommandResult {
  id: number;
  createdAt: string;
}

export interface TokenSavingsReport {
  totalAvailableTokens: number;
  selectedContextTokens: number;
  savedTokens: number;
  savingsPercent: number;
}
