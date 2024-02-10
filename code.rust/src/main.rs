// first steps with rust - only for testing

use std::process::{Command, ExitStatus};

fn run(command: &str, args: &[&str]) -> Result<String, String> {
    let output = Command::new(command)
        .args(args)
        .output()
        .map_err(|e| format!("Failed to execute command: {}", e))?;

    if output.status.success() {
        let stdout_str = String::from_utf8_lossy(&output.stdout);
        Ok(stdout_str.to_string())
    } else {
        let stderr_str = String::from_utf8_lossy(&output.stderr);
        Err(format!("Error: {}", stderr_str))
    }
}

fn main() {
    let command = "ls";
    let args = ["-l"];

    match run(command, &args) {
        Ok(output) => println!("Output: {}", output),
        Err(error) => eprintln!("{}", error),
    }
}
