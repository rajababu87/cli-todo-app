from typing import Optional

import typer

from todo.models import Todo
from todo.storage import load_todos, next_id, save_todos
from todo.utils import print_table

app = typer.Typer(help="📝  A simple CLI Todo App")

PRIORITIES = ["low", "medium", "high"]


# ── ADD ──────────────────────────────────────────────────────────────────────

@app.command()
def add(
    title: str = typer.Argument(..., help="Title of the todo"),
    priority: str = typer.Option("medium", "-p", "--priority", help="low | medium | high"),
    due: Optional[str] = typer.Option(None, "-d", "--due", help="Due date (YYYY-MM-DD)"),
):
    """Add a new todo item."""
    if priority not in PRIORITIES:
        typer.echo(f"❌  Invalid priority '{priority}'. Choose from: {PRIORITIES}")
        raise typer.Exit(1)

    todos = load_todos()
    todo = Todo(id=next_id(todos), title=title, priority=priority, due_date=due)
    todos.append(todo)
    save_todos(todos)
    typer.echo(f"✅  Added: [{todo.id}] {todo.title} ({priority})")


# ── LIST ─────────────────────────────────────────────────────────────────────

@app.command(name="list")
def list_todos(
    all: bool = typer.Option(False, "-a", "--all", help="Show completed todos too"),
    priority: Optional[str] = typer.Option(None, "-p", "--priority", help="Filter by priority"),
):
    """List todos (pending by default)."""
    todos = load_todos()
    if not all:
        todos = [t for t in todos if not t.done]
    if priority:
        todos = [t for t in todos if t.priority == priority]
    print_table(todos)


# ── COMPLETE ──────────────────────────────────────────────────────────────────

@app.command()
def complete(
    todo_id: int = typer.Argument(..., help="ID of the todo to mark complete"),
):
    """Mark a todo as done."""
    todos = load_todos()
    for t in todos:
        if t.id == todo_id:
            t.done = True
            save_todos(todos)
            typer.echo(f"✅  Marked [{todo_id}] as done.")
            return
    typer.echo(f"❌  Todo with ID {todo_id} not found.")
    raise typer.Exit(1)


# ── DELETE ────────────────────────────────────────────────────────────────────

@app.command()
def delete(
    todo_id: int = typer.Argument(..., help="ID of the todo to delete"),
    force: bool = typer.Option(False, "-f", "--force", help="Skip confirmation"),
):
    """Delete a todo item."""
    todos = load_todos()
    target = next((t for t in todos if t.id == todo_id), None)
    if not target:
        typer.echo(f"❌  Todo with ID {todo_id} not found.")
        raise typer.Exit(1)

    if not force:
        confirm = typer.confirm(f"Delete '{target.title}'?")
        if not confirm:
            typer.echo("Aborted.")
            return

    todos = [t for t in todos if t.id != todo_id]
    save_todos(todos)
    typer.echo(f"🗑️   Deleted [{todo_id}] {target.title}")


# ── EDIT ──────────────────────────────────────────────────────────────────────

@app.command()
def edit(
    todo_id: int = typer.Argument(..., help="ID of the todo to edit"),
    title: Optional[str] = typer.Option(None, "-t", "--title"),
    priority: Optional[str] = typer.Option(None, "-p", "--priority"),
    due: Optional[str] = typer.Option(None, "-d", "--due"),
):
    """Edit an existing todo."""
    todos = load_todos()
    for t in todos:
        if t.id == todo_id:
            if title:
                t.title = title
            if priority:
                if priority not in PRIORITIES:
                    typer.echo(f"❌  Invalid priority.")
                    raise typer.Exit(1)
                t.priority = priority
            if due:
                t.due_date = due
            save_todos(todos)
            typer.echo(f"✏️   Updated [{todo_id}]")
            return
    typer.echo(f"❌  Todo with ID {todo_id} not found.")
    raise typer.Exit(1)


# ── STATS ─────────────────────────────────────────────────────────────────────

@app.command()
def stats():
    """Show summary statistics."""
    todos = load_todos()
    total = len(todos)
    done = sum(1 for t in todos if t.done)
    pending = total - done
    high = sum(1 for t in todos if t.priority == "high" and not t.done)

    typer.echo(f"\n📊  Todo Stats")
    typer.echo(f"   Total   : {total}")
    typer.echo(f"   Done    : {done}")
    typer.echo(f"   Pending : {pending}")
    typer.echo(f"   High ⚠️  : {high}\n")


if __name__ == "__main__":
    app()
