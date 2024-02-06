
fn getenv(var:&str) -> String {
    // short way for getting environment value
    match std::env::var(var) {
        Ok(value) => value,
        Err(_) => "__undefined__".to_string() }}
        
mod run {
    use std::process::Command;

    const npmb: &str = "/usr/bin/npm";
    const cargo: &str = "/usr/bin/cargo";
    const poetry: &str = "~/.local/bin/poetry";

    pub fn npm(args) {
        Command::new(npm).args(args); }

    pub fn cargo(args) {
        Command::new(cargo).args(args); }

    pub fn poetry(args) {
        Command::new(poetry)
        .current_dir("~/.sweet/sweetheart/programs/my_python")
        .args(args); }
}

fn main() {
    let show = run::poetry(["show"]).output();
    println!("{:?}",show);
}
