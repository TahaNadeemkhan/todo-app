from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from todo_app.service.dto import TaskDTO
from todo_app.domain.task import TaskStatus, TaskPriority
from todo_app.domain.audit import AuditLogEntry


# Priority styling inspired by Todoist
PRIORITY_STYLES = {
    TaskPriority.HIGH: ("red", "!!!"),      # P1 - Urgent
    TaskPriority.MEDIUM: ("yellow", "!! "),  # P2 - Normal
    TaskPriority.LOW: ("blue", "!  "),       # P3 - Low
}


class ConsoleRenderer:
    def __init__(self, console: Optional[Console] = None) -> None:
        self.console = console or Console()

    def render_task_list(self, tasks: List[TaskDTO]) -> None:
        if not tasks:
            self.console.print(
                Panel("No tasks found. Try 'add' to create one or 'demo' for sample data.",
                      title="Info", style="blue")
            )
            return

        table = Table(title="Todo List", show_lines=False)
        table.add_column("ID", style="cyan", no_wrap=True, width=8)
        table.add_column("Pri", justify="center", width=3)
        table.add_column("Title", style="white", min_width=20)
        table.add_column("Status", justify="center", width=12)
        table.add_column("Created", justify="right", style="dim", width=16)

        # Sort by priority (HIGH first) then by created_at
        priority_order = {TaskPriority.HIGH: 0, TaskPriority.MEDIUM: 1, TaskPriority.LOW: 2}
        sorted_tasks = sorted(tasks, key=lambda t: (priority_order[t.priority], t.created_at))

        for task in sorted_tasks:
            # Status styling
            if task.status == TaskStatus.COMPLETED:
                status_display = "[green]✓ DONE[/]"
                title_display = f"[dim strikethrough]{task.title}[/]"
            else:
                status_display = "[yellow]○ PENDING[/]"
                title_display = task.title

            # Priority styling
            pri_style, pri_icon = PRIORITY_STYLES[task.priority]

            table.add_row(
                task.short_id,
                f"[{pri_style}]{pri_icon}[/]",
                title_display,
                status_display,
                task.created_at.strftime("%Y-%m-%d %H:%M")
            )

        self.console.print(table)

        # Show legend
        self.console.print(
            "[dim]Priority: [red]!!![/] High  [yellow]!![/] Medium  [blue]![/] Low[/]",
            justify="right"
        )

    def render_audit_log(self, entries: List[AuditLogEntry]) -> None:
        if not entries:
            self.console.print(
                Panel("No history found", title="Info", style="blue")
            )
            return

        table = Table(title="Audit Log")
        table.add_column("Timestamp", style="dim")
        table.add_column("Action", style="cyan")
        table.add_column("Details", style="white")

        for entry in entries:
            table.add_row(
                entry.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                entry.action,
                entry.details
            )
        self.console.print(table)