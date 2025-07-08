"""Handles all NLP processing tasks."""
import typer
from rich.console import Console
from nlp.pain_detector import BasicPainDetector, AdvancedPainDetector
from data.database import get_unprocessed_posts, get_unprocessed_comments, save_pain_points, PainPoint
from typing_extensions import Annotated

console = Console()

def process(
    advanced: Annotated[bool, typer.Option("--advanced", help="Use advanced NLP model.")] = False
):
    """
    Processes unprocessed data to find pain points.
    """
    console.print("[bold green]Starting NLP processing for pain points...[/bold green]")
    try:
        if advanced:
            detector = AdvancedPainDetector()
            console.print("[bold blue]Using advanced pain point detector.[/bold blue]")
        else:
            detector = BasicPainDetector()
            console.print("[bold blue]Using basic pain point detector.[/bold blue]")

        posts = get_unprocessed_posts()
        comments = get_unprocessed_comments()
        
        console.print(f"Processing {len(posts)} new posts and {len(comments)} new comments...")
        
        pain_points_to_save = []

        for post in posts:
            try:
                full_text = (post.title or "") + " " + (post.content or "")
                if not full_text.strip():
                    continue
                extracted = detector.extract_pain_points(full_text)
                for pp in extracted:
                    pain_points_to_save.append(
                        PainPoint(
                            source_id=post.id,
                            source_type='post',
                            content=pp['content'],
                            severity_score=pp.get('confidence', 0.5),
                            confidence_score=pp.get('confidence', 0.5)
                        )
                    )
            except Exception as e:
                console.print(f"[bold red]Failed to process post {post.id}: {e}[/bold red]")

        for comment in comments:
            try:
                if not comment.content or not comment.content.strip():
                    continue
                extracted = detector.extract_pain_points(comment.content)
                for pp in extracted:
                    pain_points_to_save.append(
                        PainPoint(
                            source_id=comment.id,
                            source_type='comment',
                            content=pp['content'],
                            severity_score=pp.get('confidence', 0.5),
                            confidence_score=pp.get('confidence', 0.5)
                        )
                    )
            except Exception as e:
                console.print(f"[bold red]Failed to process comment {comment.id}: {e}[/bold red]")

        if pain_points_to_save:
            save_pain_points(pain_points_to_save)
            console.print(f"[bold green]Successfully detected and saved {len(pain_points_to_save)} new pain points.[/bold green]")
        else:
            console.print("[bold yellow]No new pain points detected.[/bold yellow]")
            
        console.print("[bold green]Pain point processing completed successfully.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]An error occurred during NLP processing: {e}[/bold red]") 