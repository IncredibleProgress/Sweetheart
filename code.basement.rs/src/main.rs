
fn env(var:&str) -> String { std::env::var(var) }
fn npm(args) -> Command { Command::new("/usr/bin/npm").args(args) }
fn cargo(args) -> Command { Command::new("/usr/bin/cargo").args(args) }

fn poetry(args) -> Command {
    Command::new("~/.local/bin/poetry")
    .current_dir("~/.sweet/sweetheart/programs/my_python")
    .args(args) }

fn main() {
    let show = poetry(["show"]).output();
    println!("{:?}",show);
}
