import sys
import shlex
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from todo_app.ui.cli import TodoApp

def show_help(console: Console) -> None:
    table = Table(title="Available Commands")
    table.add_column("Command", style="cyan")
    table.add_column("Usage", style="yellow")
    table.add_column("Description", style="white")
    
    table.add_row("add", "add", "Add a new task (interactive)")
    table.add_row("add (quick)", "add <title> [desc]", "Add a new task (quick)")
    table.add_row("list", "list", "List all tasks")
    table.add_row("complete", "complete <id>", "Mark a task as complete")
    table.add_row("update", "update <id>", "Update task (interactive)")
    table.add_row("delete", "delete <id>", "Delete a task")
    table.add_row("clear", "clear", "Delete ALL tasks")
    table.add_row("undo", "undo", "Undo last action")
    table.add_row("history", "history", "View session history")
    table.add_row("help", "help", "Show this help")
    table.add_row("exit", "exit", "Exit the application")
    
    console.print(table)

def handle_command(app: TodoApp, args: list[str]) -> bool:
    if not args:
        return False
        
    cmd = args[0].lower()
    
    if cmd in ("exit", "quit"):
        app.console.print("[bold blue]Goodbye![/]")
        return True
        
    if cmd == "help":
        show_help(app.console)
        return False

    try:
        if cmd == "add":
            if len(args) < 2:
                # Interactive mode if no args provided
                app.add_task_interactive()
            else:
                title = args[1]
                desc = args[2] if len(args) > 2 else None
                app.add_task(title, desc)
                
        elif cmd in ("list", "ls"):
            app.list_tasks()
            
        elif cmd == "complete":
            if len(args) < 2:
                 app.console.print("[red]Usage: complete <id>[/]")
            else:
                app.complete_task(args[1])
                
        elif cmd == "update":
            if len(args) < 2:
                 app.console.print("[red]Usage: update <id> (or interactive update if only ID provided)[/]")
            else:
                # If only ID is provided, use interactive update
                if len(args) == 2:
                    app.update_task_interactive(args[1])
                else:
                    # Quick update
                    task_id = args[1]
                    title = args[2] if args[2] else None
                    desc = args[3] if len(args) > 3 else None
                    app.update_task(task_id, title=title, description=desc)
                
        elif cmd in ("delete", "rm"):
            if len(args) < 2:
                 app.console.print("[red]Usage: delete <id>[/]")
            else:
                app.delete_task(args[1])

        elif cmd == "clear":
            app.clear_all()
                
        elif cmd == "undo":
            app.undo()
            
        elif cmd in ("history", "log"):
            app.history()
            
        else:
            app.console.print(f"[red]Unknown command: {cmd}. Type 'help' for available commands.")

    except Exception as e:
        app.console.print(f"[red]Unexpected Error: {e}[/]")

    return False

def main() -> None:
    console = Console()
    app = TodoApp(console)
    
    # One-shot mode via args
    if len(sys.argv) > 1:
        handle_command(app, sys.argv[1:])
        return

    # Interactive mode
    console.print(Panel("Welcome to Todo App! Type 'help' for commands.", title="Todo App", style="bold blue"))
    show_help(console)
    
    while True:
        try:
            user_input = console.input("[bold green]todo>[/] ")
            if not user_input.strip():
                continue
            parts = shlex.split(user_input)
            if handle_command(app, parts):
                break
        except KeyboardInterrupt:
            console.print("\n[bold blue]Goodbye![/]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/]")

if __name__ == "__main__":
    main()