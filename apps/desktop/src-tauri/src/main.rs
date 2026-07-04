use serde::Serialize;
use std::path::PathBuf;
use std::process::Command;
use std::time::Instant;

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct CommandResult {
    status: String,
    command: String,
    args: Vec<String>,
    stdout: String,
    stderr: String,
    exit_code: Option<i32>,
    duration_ms: Option<u128>,
}

#[tauri::command]
fn run_context_command(args: Vec<String>) -> CommandResult {
    let repo_root = resolve_repo_root();
    let command_text = format_display_command(&args);

    if let Err(message) = validate_args(&args) {
        return CommandResult {
            status: "error".to_string(),
            command: command_text,
            args,
            stdout: String::new(),
            stderr: message,
            exit_code: None,
            duration_ms: Some(0),
        };
    }

    let started_at = Instant::now();
    let output = Command::new("python")
        .args(["-m", "contextos.cli.main"])
        .args(&args)
        .current_dir(&repo_root)
        .output();
    let duration_ms = Some(started_at.elapsed().as_millis());

    match output {
        Ok(output) => {
            CommandResult {
                status: if output.status.success() {
                    "success".to_string()
                } else {
                    "error".to_string()
                },
                command: command_text,
                args,
                stdout: String::from_utf8_lossy(&output.stdout).to_string(),
                stderr: String::from_utf8_lossy(&output.stderr).to_string(),
                exit_code: output.status.code(),
                duration_ms,
            }
        }
        Err(error) => CommandResult {
            status: "error".to_string(),
            command: command_text,
            args,
            stdout: String::new(),
            stderr: format!("Failed to run Python CLI: {}", error),
            exit_code: None,
            duration_ms,
        },
    }
}

fn validate_args(args: &[String]) -> Result<(), String> {
    let Some(command) = args.first().map(String::as_str) else {
        return Err("No command provided.".to_string());
    };

    match command {
        "import" => validate_import(args),
        "search" => validate_search(args),
        "ask" => validate_ask(args),
        "optimize" => validate_optimize(args),
        "stats" => validate_stats(args),
        "benchmark" => validate_benchmark(args),
        _ => Err(format!("Command is not approved for desktop: {}", command)),
    }
}

fn validate_import(args: &[String]) -> Result<(), String> {
    require_value(args, 1, "Import path is required.")?;
    validate_positional_count(args, 2)?;
    validate_allowed_flags(args, &["--db-path"])
}

fn validate_search(args: &[String]) -> Result<(), String> {
    require_value(args, 1, "Search query is required.")?;
    validate_positional_count(args, 2)?;
    validate_allowed_flags(args, &["--top-k", "--db-path"])
}

fn validate_ask(args: &[String]) -> Result<(), String> {
    require_value(args, 1, "Question is required.")?;
    validate_positional_count(args, 2)?;
    validate_allowed_flags(args, &["--dry-run", "--adapter", "--budget", "--top-k", "--db-path"])?;

    let has_dry_run = args.iter().any(|arg| arg == "--dry-run");
    let adapter_is_mock = args
        .windows(2)
        .any(|pair| pair[0] == "--adapter" && pair[1] == "mock");

    if !has_dry_run && !adapter_is_mock {
        return Err("Desktop ask only allows --dry-run or --adapter mock.".to_string());
    }
    if args
        .windows(2)
        .any(|pair| pair[0] == "--adapter" && pair[1] != "mock")
    {
        return Err("Desktop ask does not allow real AI adapters.".to_string());
    }
    Ok(())
}

fn validate_optimize(args: &[String]) -> Result<(), String> {
    require_value(args, 1, "Document id or filepath is required.")?;
    validate_positional_count(args, 2)?;
    validate_allowed_flags(args, &["--level", "--db-path"])?;

    if let Some(level) = flag_value(args, "--level") {
        match level {
            "light" | "medium" | "aggressive" => Ok(()),
            _ => Err("Optimize level must be light, medium, or aggressive.".to_string()),
        }
    } else {
        Err("Optimize level is required.".to_string())
    }
}

fn validate_stats(args: &[String]) -> Result<(), String> {
    validate_positional_count(args, 1)?;
    validate_allowed_flags(args, &["--db-path"])
}

fn validate_benchmark(args: &[String]) -> Result<(), String> {
    validate_positional_count(args, 1)?;
    validate_allowed_flags(
        args,
        &[
            "--dataset",
            "--db-path",
            "--output",
            "--query",
            "--question",
            "--iterations",
        ],
    )?;

    match flag_value(args, "--iterations") {
        Some(value) => value
            .parse::<u32>()
            .map_err(|_| "Benchmark iterations must be a positive integer.".to_string())
            .and_then(|iterations| {
                if iterations == 0 {
                    Err("Benchmark iterations must be at least 1.".to_string())
                } else {
                    Ok(())
                }
            }),
        None => Err("Benchmark iterations are required.".to_string()),
    }
}

fn require_value(args: &[String], index: usize, message: &str) -> Result<(), String> {
    if args.get(index).map(|value| value.trim().is_empty()).unwrap_or(true) {
        Err(message.to_string())
    } else {
        Ok(())
    }
}

fn validate_allowed_flags(args: &[String], allowed_flags: &[&str]) -> Result<(), String> {
    let mut index = 1;
    while index < args.len() {
        let arg = &args[index];
        if arg.starts_with("--") {
            if !allowed_flags.contains(&arg.as_str()) {
                return Err(format!("Flag is not approved for desktop: {}", arg));
            }
            if flag_requires_value(arg) {
                if args
                    .get(index + 1)
                    .map(|value| value.starts_with("--") || value.trim().is_empty())
                    .unwrap_or(true)
                {
                    return Err(format!("Flag requires a value: {}", arg));
                }
                index += 2;
                continue;
            }
        }
        index += 1;
    }
    Ok(())
}

fn validate_positional_count(args: &[String], max_positionals: usize) -> Result<(), String> {
    let mut positionals = 0;
    let mut index = 0;
    while index < args.len() {
        let arg = &args[index];
        if arg.starts_with("--") {
            index += if flag_requires_value(arg) { 2 } else { 1 };
            continue;
        }
        positionals += 1;
        if positionals > max_positionals {
            return Err("Unexpected positional argument for desktop command.".to_string());
        }
        index += 1;
    }
    Ok(())
}

fn flag_requires_value(flag: &str) -> bool {
    matches!(
        flag,
        "--adapter"
            | "--budget"
            | "--dataset"
            | "--db-path"
            | "--iterations"
            | "--level"
            | "--output"
            | "--query"
            | "--question"
            | "--top-k"
    )
}

fn flag_value<'a>(args: &'a [String], flag: &str) -> Option<&'a str> {
    args.windows(2)
        .find(|pair| pair[0] == flag)
        .map(|pair| pair[1].as_str())
}

fn format_display_command(args: &[String]) -> String {
    let rendered_args = args
        .iter()
        .map(|arg| {
            if arg.contains(' ') {
                format!("\"{}\"", arg.replace('"', "\\\""))
            } else {
                arg.to_string()
            }
        })
        .collect::<Vec<_>>()
        .join(" ");
    format!("python -m contextos.cli.main {}", rendered_args)
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
