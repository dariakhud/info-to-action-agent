"""CLI presentation layer for agent commands as Typer app."""
import datetime
import typer
from typing import Optional, List, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich import box

from src.modules.agent.service.agent import AgentService
from src.modules.agent.dto import ContentDTO, SummaryDTO, ScheduledEventDTO

# Global console instance for rich output
console = Console()

# Create typer app for agent commands
app = typer.Typer(help="Agent commands for information-to-action workflow")


@app.command(name="run")
def run_agent_command(
    url: Optional[str] = typer.Option(None, "--url", "-u", help="URL to an article or YouTube video"),
    text: Optional[str] = typer.Option(None, "--text", "-t", help="Direct text input"),
    auto_schedule: bool = typer.Option(False, "--auto-schedule", help="Auto-schedule all actions without asking")
):
    """Run the full agent workflow: summarize, extract actions, and schedule."""
    agent_service = AgentService()
    
    # Welcome
    welcome_text = """
    [bold cyan]Information-to-Action Agent[/bold cyan]
    
    This agent will:
    • Summarize your content
    • Extract actionable tasks
    • Help you schedule them in Google Calendar
    """
    console.print(Panel.fit(welcome_text, border_style="cyan"))
    console.print()
    
    # Get input
    if url:
        user_input = url
    elif text:
        user_input = text
    else:
        console.print("[dim]Enter one of the following:[/dim]")
        console.print("[dim]  1. Direct text you want summarized[/dim]")
        console.print("[dim]  2. URL to an online article[/dim]")
        console.print("[dim]  3. URL to a YouTube video[/dim]")
        user_input = Prompt.ask(
            "[bold]Your input[/bold]",
            default=""
        ).strip()
    
    if not user_input:
        console.print("[yellow]Empty input. Exiting.[/yellow]")
        return
    
    # Determine if input is URL or text
    from src.infra.client.content_fetcher import is_url
    if url or (user_input and is_url(user_input)):
        input_url = url if url else user_input
        input_text = None
    else:
        input_url = None
        input_text = text if text else user_input
    
    # Fetch content
    try:
        with console.status("[cyan]Fetching content...[/cyan]", spinner="dots"):
            content = agent_service.process_content(url=input_url, text=input_text)
        console.print(
            f"[green]✓ Extracted {len(content.text)} characters from {content.source_type}[/green]"
        )
    except ValueError as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        return
    
    # Summarize
    try:
        with console.status("[cyan]Summarizing text with AI...[/cyan]", spinner="dots"):
            summary = agent_service.summarize(content)
        console.print()
        console.print(Panel.fit(
            "[bold cyan]Summary Points[/bold cyan]",
            border_style="cyan"
        ))
        console.print(Markdown(summary.points))
        console.print()
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] Failed to summarize: {e}")
        return
    
    # Extract actions
    try:
        with console.status("[cyan]Extracting actionable tasks with AI...[/cyan]", spinner="dots"):
            actions = agent_service.extract_actions(summary)
        console.print(Panel.fit(
            "[bold cyan]Extracted Actionable Tasks[/bold cyan]",
            border_style="cyan"
        ))
        
        # Create table for actions
        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("#", style="dim", width=3)
        table.add_column("Action", style="white")
        
        for i, action in enumerate(actions, 1):
            table.add_row(str(i), action)
        
        console.print(table)
        console.print()
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] Failed to extract actions: {e}")
        return
    
    # Schedule actions
    if auto_schedule:
        console.print("[yellow]Auto-scheduling all actions for default time (today 10:00)[/yellow]")
        now = datetime.datetime.now()
        default_time = now.replace(hour=10, minute=0, second=0, microsecond=0)
        confirmed = [(action, default_time) for action in actions]
    else:
        console.print()
        console.print(Panel.fit("[bold cyan]Scheduling Actions[/bold cyan]", border_style="cyan"))
        confirmed = []
        
        for i, action in enumerate(actions, 1):
            console.print(f"\n[bold yellow]Action {i}/{len(actions)}:[/bold yellow] [white]{action}[/white]")
            choice = Confirm.ask("Do you want to schedule this action?", default=True)
            
            if choice:
                default_time = datetime.datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
                default_str = default_time.strftime("%Y-%m-%d %H:%M")
                time_str = Prompt.ask(
                    "Enter start time",
                    default=default_str
                )
                
                if not time_str or time_str == default_str:
                    start_time = default_time
                else:
                    try:
                        start_time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M")
                        if start_time < datetime.datetime.now():
                            console.print("[yellow]Warning: Time is in the past. Using default time.[/yellow]")
                            start_time = default_time
                    except ValueError:
                        console.print("[red]Invalid format. Using default time (today 10:00).[/red]")
                        start_time = default_time
                
                confirmed.append((action, start_time))
                console.print(f"[green]✓ Scheduled for {start_time.strftime('%Y-%m-%d %H:%M')}[/green]")
    
    if confirmed:
        console.print()
        for action, start_time in confirmed:
            try:
                with console.status(f"[cyan]Adding '{action}' to calendar...[/cyan]", spinner="dots"):
                    event = agent_service.schedule_action(action, start_time)
                if event.event_link:
                    console.print(
                        f"[green]✓ Event created:[/green] [link={event.event_link}]{event.event_link}[/link]"
                    )
                else:
                    console.print(f"[green]✓ Event created for {event.start_time.strftime('%Y-%m-%d %H:%M')}[/green]")
            except Exception as e:
                console.print(f"[red]✗ Error:[/red] Failed to schedule action: {e}")
    else:
        console.print("[yellow]No actions scheduled.[/yellow]")
    
    console.print()
    console.print(Panel.fit("[bold green]Processing complete. Thank you![/bold green]", border_style="green"))
