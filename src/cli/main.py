"""
CLI interface for FC26 Career Analyzer.
"""

import sys

import typer
from rich.console import Console
from rich.prompt import Prompt
from typing import Optional

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
    question: Optional[str] = typer.Argument(
        None,
        help="Pergunta sobre seu save (opcional, inicia modo interativo se omitido)",
    ),
    context_type: str = typer.Option(
        "top_players",
        "--context",
        "-c",
        help="Tipo de contexto: summary, top_players, filtered",
    ),
    limit: int = typer.Option(
        10, "--limit", "-l", help="Número máximo de jogadores no contexto"
    ),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        "-i",
        help="Forçar modo interativo mesmo com pergunta fornecida",
    ),
):
    """
    Faça perguntas sobre seu save usando IA (Gemini).

    Exemplos:
        fc26-analyzer query "quem é meu melhor jogador?"
        fc26-analyzer query "jogadores jovens com potencial alto"
        fc26-analyzer query --interactive
    """
    from ..database.models import get_db
    from rich.panel import Panel

    db = next(get_db())

    # Modo interativo se não forneceu pergunta ou se --interactive
    if question is None or interactive:
        console.print(
            Panel.fit(
                "[bold cyan]🤖 FC26 Career Analyzer - Modo Interativo[/bold cyan]\n\n"
                "Faça perguntas sobre seu save em linguagem natural.\n"
                "Digite 'sair' ou 'exit' para encerrar.\n"
                "Digite 'limpar' para resetar o contexto.",
                border_style="cyan",
            )
        )

        # Loop interativo
        while True:
            try:
                user_question = Prompt.ask("\n[bold yellow]Você[/bold yellow]")

                if user_question.lower() in ["sair", "exit", "quit"]:
                    console.print("[dim]Encerrando...[/dim]")
                    break

                if user_question.lower() in ["limpar", "clear", "reset"]:
                    console.print("[dim]Contexto resetado.[/dim]")
                    continue

                # Processar pergunta
                _process_query(db, user_question, context_type, limit)

            except KeyboardInterrupt:
                console.print("\n[dim]Encerrando...[/dim]")
                break
    else:
        # Modo direto
        _process_query(db, question, context_type, limit)


def _process_query(db, question: str, context_type: str, limit: int):
    """Helper function to process a single query."""
    from ..llm import GeminiClient, ContextBuilder, PromptBuilder
    from ..core.query_router import QueryRouter
    from rich.panel import Panel
    from rich.markdown import Markdown
    import os

    # Try SQL router first
    router = QueryRouter(db)
    source, sql_result, gemini_query = router.route(question)

    if source == "sql":
        # SQL handled it
        console.print()
        console.print(
            Panel(
                Markdown(sql_result),
                title="[bold blue]⚡ Resposta Rápida (SQL)[/bold blue]",
                border_style="blue",
                padding=(1, 2),
            )
        )
        console.print("[dim]Fonte: SQL direto (sem custo API)[/dim]")
        return

    # Gemini needed
    # Verificar API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        console.print("[bold red]❌ GEMINI_API_KEY não configurada no .env[/bold red]")
        raise typer.Exit(1)

    try:
        # Build context
        with console.status("[bold yellow]Preparando contexto...[/bold yellow]"):
            context_builder = ContextBuilder(db)
            context = context_builder.build_context(context_type, limit=limit)

        # Build prompt
        prompt_builder = PromptBuilder()
        prompt, system_instruction = prompt_builder.build_prompt(question, context)

        # Query Gemini
        with console.status("[bold yellow]Consultando IA...[/bold yellow]"):
            client = GeminiClient(api_key)
            result = client.query(prompt, system_instruction)
            response = result.get("text", "⚠️ Erro ao gerar resposta da IA.")

        # Display response
        console.print()
        console.print(
            Panel(
                Markdown(response),
                title="[bold green]🤖 Resposta da IA (Gemini)[/bold green]",
                border_style="green",
                padding=(1, 2),
            )
        )

        # Context info
        console.print(
            f"\n[dim]Contexto usado: {context_type} | Tamanho: {len(context)} chars[/dim]"
        )

    except Exception as e:
        console.print(f"[bold red]❌ Erro ao processar query:[/bold red] {str(e)}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
