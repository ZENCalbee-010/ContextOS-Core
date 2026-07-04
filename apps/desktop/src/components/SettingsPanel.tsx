import { Panel } from "./Panel";

interface SettingsPanelProps {
  theme: "light" | "dark";
  onThemeChange: (theme: "light" | "dark") => void;
}

export function SettingsPanel({ theme, onThemeChange }: SettingsPanelProps) {
  return (
    <Panel title="Settings">
      <p className="panel-copy">Local desktop preferences and runtime paths for the CLI wrapper.</p>
      <label>
        Theme
        <select value={theme} onChange={(event) => onThemeChange(event.target.value as "light" | "dark")}>
          <option value="light">Light</option>
          <option value="dark">Dark</option>
        </select>
      </label>
      <div className="settings-list">
        <div>
          <span>CLI backend</span>
          <strong>python -m contextos.cli.main</strong>
        </div>
        <div>
          <span>Desktop database</span>
          <strong>data/desktop.db</strong>
        </div>
        <div>
          <span>Retrieval</span>
          <strong>BM25 only</strong>
        </div>
        <div>
          <span>AI mode</span>
          <strong>Dry-run / mock</strong>
        </div>
      </div>
    </Panel>
  );
}
