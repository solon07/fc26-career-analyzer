"""
CLI interface for FC26 Career Analyzer.
"""

import sys

import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from src.llm import GeminiClient, PromptBuilder, ContextBuilder

from src.core.importer import importer

app = typer.Typer(help="FC26 Career Analyzer - AI-powered career mode analysis")

# Force UTF-8 for console output to support emojis/special chars on Windows
try:
    if sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    # For older python versions or if reconfigure not available
    pass

console = Console()


@app.command(name="import")
def import_save(
    save_path: str = typer.Argument(
        None,
        help="Path to FC 26 save file (optional, uses .env default if not provided)",
    ),
):
    """
    Import FC 26 save file into database.

    Example:
        python -m src.cli.main import
        python -m src.cli.main import "C:\\path\\to\\save\\CmMgrC..."
    """
    try:
        stats = importer.import_save(save_path)

        console.print("\n[green]Import successful![/green]\n")
        console.print(
            f"Players in database: {stats['players_imported'] + stats['players_updated']}"
        )

    except Exception as e:
        console.print(f"\n[red]Import failed: {e}[/red]\n")
        raise typer.Exit(code=1)


@app.command()
def info():
    """
    Show database information and statistics.
    """
    from src.database.models import SessionLocal, Player

    db = SessionLocal()

    try:
        # Get stats
        total_players = db.query(Player).count()

        if total_players == 0:
            console.print("[yellow]⚠️  No data found. Run 'import' first.[/yellow]")
            return

        # Header
        console.print(
            "\n[bold cyan]═══════════════════════════════════════[/bold cyan]"
        )
        console.print("[bold cyan]   FC26 CAREER ANALYZER - INFO[/bold cyan]")
        console.print(
            "[bold cyan]═══════════════════════════════════════[/bold cyan]\n"
        )

        # Database stats
        console.print(f"[green]📊 Total Players:[/green] {total_players}")

        # Top players by OVR
        console.print("\n[cyan]🏆 Top 10 Players by Overall Rating:[/cyan]\n")

        top_players = (
            db.query(Player)
            .filter(Player.overallrating.isnot(None))
            .order_by(Player.overallrating.desc())
            .limit(10)
            .all()
        )

        for i, player in enumerate(top_players, 1):
            console.print(f"  {i:2d}. {player.detailed_display}")

        # Sample of players with resolved names
        console.print("\n[cyan]✨ Players with Resolved Names:[/cyan]\n")

        named_players = (
            db.query(Player).filter(~Player.firstname.like("Unknown_%")).limit(5).all()
        )

        if named_players:
            for player in named_players:
                console.print(f"  • {player.detailed_display}")
        else:
            console.print("  [yellow]⚠️  No players with resolved names found[/yellow]")

        # Name resolution stats
        total_named = (
            db.query(Player).filter(~Player.firstname.like("Unknown_%")).count()
        )
        total_unknown = total_players - total_named

        console.print("\n[cyan]📋 Name Resolution Statistics:[/cyan]")
        console.print(f"  • Resolved names: [green]{total_named}[/green]")
        console.print(f"  • Unknown (fallback): [yellow]{total_unknown}[/yellow]")

        # Note about limitation
        if total_unknown > 0:
            console.print(
                "\n[dim]ℹ️  Note: Base game players appear as 'Player #ID' because"
            )
            console.print(
                "   their names are stored in the game's internal database,[/dim]"
            )
            console.print(
                "[dim]   not in the save file. This will be enhanced in a future update.[/dim]"
            )

        console.print(
            "\n[bold cyan]═══════════════════════════════════════[/bold cyan]\n"
        )

    finally:
        db.close()


@app.command()
def query(
    question: str = typer.Argument(None, help="Pergunta sobre sua carreira (opcional)"),
):
    """
    Faça perguntas sobre sua carreira usando IA (Gemini)

    Exemplos:
        python -m src.cli.main query "Quais são os 5 melhores jogadores?"
        python -m src.cli.main query  # Modo interativo
    """
    from src.database.models import SessionLocal, Player

    db = SessionLocal()

    try:
        # Initialize LLM components
        try:
            client = GeminiClient()
            builder = ContextBuilder(db)
        except ValueError as e:
            console.print(f"\n[bold red]Erro de configuração:[/bold red] {e}")
            console.print(
                "\n[yellow]Verifique se GEMINI_API_KEY está configurada no arquivo .env[/yellow]"
            )
            return
        except Exception as e:
            console.print(f"\n[bold red]Erro ao inicializar Gemini:[/bold red] {e}")
            return

        # Interactive mode if no question provided
        if question is None:
            _interactive_query_mode(client, builder, db)
        else:
            # Direct query mode
            _process_single_query(question, client, builder)

    finally:
        db.close()


def _interactive_query_mode(client: GeminiClient, builder: ContextBuilder, db):
    """Interactive query loop"""
    from src.database.models import Player

    console.print("\n[bold cyan]═══════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]   FC26 CAREER ANALYZER - QUERY IA[/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════[/bold cyan]\n")

    console.print("[dim]Faça perguntas sobre sua carreira em linguagem natural.[/dim]")
    console.print("[dim]Digite 'sair' ou 'exit' para encerrar.[/dim]\n")

    # Show quick stats
    total_players = db.query(Player).count()
    console.print(f"[green]Dados carregados:[/green] {total_players} jogadores\n")

    # Query loop
    query_count = 0
    while True:
        try:
            # Get user input
            console.print("[bold cyan]Sua pergunta:[/bold cyan] ", end="")
            user_question = input().strip()

            # Check exit commands
            if user_question.lower() in ["sair", "exit", "quit", "q"]:
                console.print("\n[yellow]Encerrando... Até logo![/yellow]\n")
                break

            # Skip empty input
            if not user_question:
                continue

            # Process query
            query_count += 1
            _process_single_query(
                user_question, client, builder, query_number=query_count
            )
            console.print()  # Empty line for spacing

        except KeyboardInterrupt:
            console.print("\n\n[yellow]Interrompido pelo usuário. Até logo![/yellow]\n")
            break
        except EOFError:
            console.print("\n\n[yellow]Entrada encerrada. Até logo![/yellow]\n")
            break


def _process_single_query(
    question: str,
    client: GeminiClient,
    builder: ContextBuilder,
    query_number: int = None,
):
    """Process a single query and display results"""

    # Show processing indicator
    if query_number:
        console.print(f"\n[dim]Query #{query_number}[/dim]")

    with console.status("[bold yellow]Analisando pergunta...[/bold yellow]"):
        try:
            # Use QueryRouter instead of manual logic
            from src.llm.query_router import QueryRouter

            router = QueryRouter(db=builder.db, gemini_client=client)
            result = router.route_query(question)

            if result["success"]:
                # Show source badge
                source_badge = {
                    "sql": "[blue]⚡ SQL[/blue]",
                    "gemini": "[green]🤖 Gemini[/green]",
                    "error": "[red]❌ Error[/red]",
                }.get(result["source"], "")

                # Display response
                _display_response(
                    question=question,
                    response_text=result["answer"],
                    tokens_used=result["tokens_used"],
                    source=source_badge,
                )
            else:
                console.print(f"\n[bold red]Erro:[/bold red] {result['answer']}")

        except Exception as e:
            console.print(f"\n[bold red]Erro inesperado:[/bold red] {e}")
            import traceback

            console.print(f"[dim]{traceback.format_exc()}[/dim]")


def _display_response(
    question: str, response_text: str, tokens_used: int, source: str = ""
):
    """Display formatted response"""

    # Create panel with question
    console.print()
    console.print(
        Panel(f"[bold]{question}[/bold]", title="Pergunta", border_style="cyan")
    )

    # Display response as markdown
    console.print()
    title = f"Resposta {source}" if source else "Resposta"
    console.print(
        Panel(
            Markdown(response_text),
            title=title,
            border_style="green",
            padding=(1, 2),
        )
    )

    # Display metadata
    if tokens_used > 0:
        console.print(
            f"\n[dim]Tokens utilizados: ~{tokens_used} | Custo: ~${tokens_used * 0.000002:.6f}[/dim]"
        )
    else:
        console.print(f"\n[dim]✨ Resposta SQL (sem custo de tokens)[/dim]")


if __name__ == "__main__":
    app()
