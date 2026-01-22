from rich.console import Console
from todo_app.ui.cli import TodoApp

def reproduce():
    console = Console()
    app = TodoApp(console)

    print("--- 1. Running Demo ---")
    app.demo()

    print("\n--- 2. Listing Tasks ---")
    tasks = app.service.list_tasks()
    if not tasks:
        print("No tasks found!")
        return

    target_task = tasks[0]
    short_id = target_task.id[:8]
    print(f"Target Task Full ID: {target_task.id}")
    print(f"Target Short ID:     {short_id}")

    print("\n--- 3. Testing Update (Interactive Logic) ---")
    # This mimics the bug in update_task_interactive where it uses repo.get() directly
    found_task = app.service.repository.get(short_id)
    if found_task:
        print(f"repo.get('{short_id}') SUCCESS (Unexpected)")
    else:
        print(f"repo.get('{short_id}') FAILED (Expected failure due to direct repo access)")

    print("\n--- 4. Testing Delete (Service Logic) ---")
    # This mimics 'delete <id>' which calls app.delete_task -> service.delete_task
    try:
        app.delete_task(short_id)
        print("app.delete_task(short_id) SUCCESS")
        
        # Verify
        remaining = app.service.list_tasks()
        if any(t.id == target_task.id for t in remaining):
            print("FAILURE: Task still in list!")
        else:
            print("VERIFIED: Task gone.")
            
    except Exception as e:
        print(f"app.delete_task(short_id) FAILED with error: {e}")

if __name__ == "__main__":
    reproduce()
