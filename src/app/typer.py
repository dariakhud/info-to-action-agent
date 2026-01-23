import typer
from typing import Optional
from src.modules.agent.commands import app as agent_app, run_agent_command


app = typer.Typer(help="Information-to-Action Agent CLI")


@app.command(name="ping")
def ping_command():
    """Test command."""
    typer.echo("pong")


@app.command(name="run")
def run_command(
    url: Optional[str] = typer.Option(None, "--url", "-u", help="URL to an article or YouTube video"),
    text: Optional[str] = typer.Option(None, "--text", "-t", help="Direct text input"),
    auto_schedule: bool = typer.Option(False, "--auto-schedule", help="Auto-schedule all actions without asking")
):
    """Run the full agent workflow: summarize, extract actions, and schedule."""
    run_agent_command(url=url, text=text, auto_schedule=auto_schedule)


# Add agent commands as a sub-app
app.add_typer(agent_app, name="agent")
