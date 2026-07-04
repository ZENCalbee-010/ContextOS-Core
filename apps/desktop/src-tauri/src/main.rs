use serde::Serialize;
use std::path::PathBuf;
use std::process::Command;

#[derive(Serialize)]
struct CommandResult {
    status: String,
    command: String,
    output: String,
}

#[tauri::command]
fn run_context_command(args: Vec<String>) -> CommandResult {
    let repo_root = resolve_repo_root();
    let command_text = format!("python -m contextos.cli.main {}", args.join(" "));

    let output = Command::new("python")
        .args(["-m", "contextos.cli.main"])
        .args(&args)
        .current_dir(&repo_root)
        .output();

    match output {
        Ok(output) => {
            let stdout = String::from_utf8_lossy(&output.stdout);
            let stderr = String::from_utf8_lossy(&output.stderr);
            let combined = format!("{}{}", stdout, stderr);
            CommandResult {
                status: if output.status.success() {
                    "success".to_string()
                } else {
                    "error".to_string()
                },
                command: command_text,
                output: combined,
            }
        }
        Err(error) => CommandResult {
            status: "error".to_string(),
            command: command_text,
            output: error.to_string(),
        },
    }
}

fn resolve_repo_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(|desktop_dir| desktop_dir.parent())
        .and_then(|apps_dir| apps_dir.parent())
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("."))
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![run_context_command])
        .run(tauri::generate_context!())
        .expect("error while running ContextOS Desktop");
}
