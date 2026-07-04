export type CommandStatus = "idle" | "running" | "success" | "error";

export interface CommandResult {
  status: CommandStatus;
  command: string;
  output: string;
}

export interface CommandLogEntry extends CommandResult {
  id: number;
  createdAt: string;
}
