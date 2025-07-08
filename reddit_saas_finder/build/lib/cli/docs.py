import typer
import subprocess
import os
from rich.console import Console
import sys

app = typer.Typer()
console = Console()

@app.command()
def build(
    ctx: typer.Context,
    clean: bool = typer.Option(False, "--clean", "-c", help="Clean the build directory before building."),
    browse: bool = typer.Option(False, "--browse", "-b", help="Open the documentation in a browser after building."),
):
    """
    Build the HTML documentation using Sphinx.
    """
    docs_dir = "docs"
    source_dir = os.path.join(docs_dir, "source")
    build_dir = os.path.join(docs_dir, "api")

    if clean:
        console.print(f"Cleaning build directory: {build_dir}")
        subprocess.run(["rm", "-rf", build_dir], check=True)

    console.print("Building documentation...")
    cmd = [
        "sphinx-build",
        "-b", "html",
        source_dir,
        build_dir
    ]
    
    try:
        # We need to use the venv sphinx-build
        venv_path = os.path.dirname(sys.executable)
        cmd[0] = os.path.join(venv_path, cmd[0])

        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        console.print(result.stdout)
        console.print(f"[bold green]Documentation built successfully.[/bold green]")
        console.print(f"You can find the documentation in: {os.path.abspath(build_dir)}/index.html")

        if browse:
            import webbrowser
            webbrowser.open(f"file://{os.path.abspath(build_dir)}/index.html")

    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Error building documentation:[/bold red]")
        console.print(e.stderr)
        raise typer.Exit(code=1)
    except FileNotFoundError:
        console.print("[bold red]Error: 'sphinx-build' command not found.[/bold red]")
        console.print("Please ensure Sphinx is installed in your environment.")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app() 