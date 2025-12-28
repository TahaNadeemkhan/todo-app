from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from todo_app.service.task_service import TaskService
from todo_app.repository.in_memory import InMemoryTaskRepository
from todo_app.domain.task import TaskPriority
from todo_app.domain.exceptions import TaskNotFoundError
from .renderer import ConsoleRenderer


class TodoApp:
    def __init__(self, console: Optional[Console] = None) -> None:
        self.console = console or Console()
        self.repository = InMemoryTaskRepository()
        self.service = TaskService(self.repository)
        self.renderer = ConsoleRenderer(self.console)

    def add_task_interactive(self) -> None:
        """Interactive task creation with prompts (like Todoist/Things)."""
        self.console.print("\n[bold cyan]Add New Task[/]")
        self.console.print("[dim]─" * 40 + "[/]\n")

        # Required: Title
        title = Prompt.ask("[bold]Title[/]")
        if not title.strip():
            self.console.print(Panel("Title cannot be empty", title="Error", style="red"))
            return

        # Optional: Description
        description = Prompt.ask("[dim]Description (optional)[/]", default="")
        description = description if description.strip() else None

        # Optional: Priority - Beautiful Selection
        self.console.print("\n[bold]Select Priority:[/]")
        self.console.print(Panel(
            "[bold red]1. High (!!!)[/]\n"
            "[bold yellow]2. Medium (!!) [dim](Default)[/][/]\n"
            "[bold blue]3. Low (!)[/]",
            title="Priority Levels",
            border_style="dim",
            width=40
        ))

        priority_input = Prompt.ask(
            "[dim]Choose priority[/]",
            choices=["1", "2", "3"],
            default="2",
            show_choices=False
        )
        priority_map = {"1": TaskPriority.HIGH, "2": TaskPriority.MEDIUM, "3": TaskPriority.LOW}
        priority = priority_map[priority_input]

        # Create task
        try:
            task_dto = self.service.create_task(title, description, priority)
            self.console.print(
                Panel(
                    f"Task '[bold]{task_dto.title}[/]' added\n"
                    f"ID: [cyan]{task_dto.short_id}[/]  "
                    f"Priority: [{'red' if priority == TaskPriority.HIGH else 'yellow' if priority == TaskPriority.MEDIUM else 'blue'}]"
                    f"{priority.value}[/]",
                    title="Success",
                    style="green"
                )
            )
        except ValueError as e:
            self.console.print(Panel(str(e), title="Error", style="red"))

    def add_task(self, title: str, description: Optional[str] = None, priority: TaskPriority = TaskPriority.MEDIUM) -> None:
        """Quick add task (non-interactive)."""
        try:
            task_dto = self.service.create_task(title, description, priority)
            self.console.print(
                Panel(
                    f"Task '[bold]{task_dto.title}[/]' added with ID [cyan]{task_dto.short_id}[/]",
                    title="Success",
                    style="green"
                )
            )
        except ValueError as e:
            self.console.print(
                Panel(str(e), title="Error", style="red")
            )

    def list_tasks(self) -> None:
        tasks = self.service.list_tasks()
        self.renderer.render_task_list(tasks)

    def complete_task(self, task_id: str) -> None:
        try:
            task = self.service.complete_task(task_id)
            self.console.print(
                Panel(
                    f"Task '{task.title}' marked as [green]COMPLETED[/green]",
                    title="Success",
                    style="green"
                )
            )
        except TaskNotFoundError as e:
             self.console.print(
                Panel(str(e), title="Error", style="red")
            )

    def update_task_interactive(self, task_id: str) -> None:
        """Interactive task update with prompts, pre-filling current values."""
        try:
            current_task = self.service.get_task(task_id)
            if not current_task:
                self.console.print(Panel(f"Task with ID {task_id} not found", title="Error", style="red"))
                return

            self.console.print(f"\n[bold cyan]Update Task:[/][dim] {current_task.short_id} - {current_task.title}[/]")
            self.console.print("[dim]─" * 40 + "[/]\n")

            new_title = Prompt.ask(
                "[bold]Title[/]",
                default=current_task.title
            )
            new_description = Prompt.ask(
                "[dim]Description (optional)[/]",
                default=current_task.description if current_task.description else ""
            )
            new_description = new_description if new_description.strip() else None

            self.console.print("\n[bold]Select Priority:[/]")
            self.console.print(Panel(
                "[bold red]1. High (!!!)[/]\n"
                "[bold yellow]2. Medium (!!) [dim](Default)[/][/]\n"
                "[bold blue]3. Low (!)[/]",
                title="Priority Levels",
                border_style="dim",
                width=40
            ))

            priority_map_inv = {
                TaskPriority.HIGH: "1",
                TaskPriority.MEDIUM: "2",
                TaskPriority.LOW: "3"
            }
            default_priority_choice = priority_map_inv[current_task.priority]

            priority_input = Prompt.ask(
                "[dim]Choose priority[/]",
                choices=["1", "2", "3"],
                default=default_priority_choice,
                show_choices=False
            )
            selected_priority = {
                "1": TaskPriority.HIGH,
                "2": TaskPriority.MEDIUM,
                "3": TaskPriority.LOW
            }[priority_input]

            title_to_update = new_title if new_title != current_task.title else None
            desc_to_update = new_description if new_description != current_task.description else None
            priority_to_update = selected_priority if selected_priority != current_task.priority else None

            if not (title_to_update or desc_to_update or priority_to_update):
                self.console.print(Panel("No changes detected, task not updated.", title="Info", style="blue"))
                return

            updated_task_dto = self.service.update_task(
                task_id,
                title=title_to_update,
                description=desc_to_update,
                priority=priority_to_update
            )
            self.console.print(
                Panel(
                    f"Task '[bold]{updated_task_dto.title}[/]' updated successfully.\n"
                    f"ID: [cyan]{updated_task_dto.short_id}[/]  "
                    f"Priority: [{'red' if updated_task_dto.priority == TaskPriority.HIGH else 'yellow' if updated_task_dto.priority == TaskPriority.MEDIUM else 'blue'}]"
                    f"{updated_task_dto.priority.value}[/]",
                    title="Success",
                    style="green"
                )
            )

        except TaskNotFoundError as e:
            self.console.print(Panel(str(e), title="Error", style="red"))
        except ValueError as e:
            self.console.print(Panel(str(e), title="Error", style="red"))
        except Exception as e:
            self.console.print(Panel(f"An unexpected error occurred during update: {e}", title="Error", style="red"))


    def update_task(self, task_id: str, title: Optional[str] = None, description: Optional[str] = None, priority: Optional[TaskPriority] = None) -> None:
        """Quick update task (non-interactive)."""
        try:
            task = self.service.update_task(task_id, title, description, priority)
            self.console.print(
                Panel(
                    f"Task '[bold]{task.title}[/]' updated",
                    title="Success",
                    style="green"
                )
            )
        except TaskNotFoundError as e:
             self.console.print(
                Panel(str(e), title="Error", style="red")
            )
        except ValueError as e:
            self.console.print(
                Panel(str(e), title="Error", style="red")
            )

    def delete_task(self, task_id: str) -> None:
        try:
            task = self.service.delete_task(task_id)
            self.console.print(
                Panel(
                    f"Task '{task.title}' deleted",
                    title="Success",
                    style="green"
                )
            )
        except TaskNotFoundError as e:
             self.console.print(
                Panel(str(e), title="Error", style="red")
            )

    def clear_all(self) -> None:
        """Clear all tasks."""
        if Confirm.ask("[bold red]Are you sure you want to delete ALL tasks?[/]"):
            self.service.clear_all_tasks()
            self.console.print(
                Panel(
                    "All tasks have been cleared.",
                    title="Success",
                    style="green"
                )
            )

    def undo(self) -> None:
        result = self.service.undo()
        if result:
             self.console.print(
                Panel(
                    f"Undid action: [yellow]{result}[/yellow]",
                    title="Undo Successful",
                    style="green"
                )
            )
        else:
             self.console.print(
                Panel("Nothing to undo", title="Info", style="blue")
            )

    def history(self) -> None:
        entries = self.service.get_history()
        self.renderer.render_audit_log(entries)