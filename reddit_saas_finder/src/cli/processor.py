"""Handles all NLP processing tasks."""
import typer
from rich import print
from reddit_saas_finder.src.nlp.pain_detector import BasicPainDetector, AdvancedPainDetector
from reddit_saas_finder.src.data.database import get_unprocessed_posts, get_unprocessed_comments, save_pain_points, PainPoint

app = typer.Typer()

def process_pain_points(use_advanced_detector=False):
    """
    Detects pain points from unprocessed posts and comments and saves them to the database.
    """
    if use_advanced_detector:
        detector = AdvancedPainDetector()
        print("[bold blue]Using advanced pain point detector.[/bold blue]")
    else:
        detector = BasicPainDetector()
        print("[bold blue]Using basic pain point detector.[/bold blue]")

    posts = get_unprocessed_posts()
    comments = get_unprocessed_comments()
    
    print(f"Processing {len(posts)} new posts and {len(comments)} new comments...")
    
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
            print(f"[bold red]Failed to process post {post.id}: {e}[/bold red]")
            # Optionally, log the full text that caused the error
            # print(f"Problematic text: {full_text}")

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
            print(f"[bold red]Failed to process comment {comment.id}: {e}[/bold red]")
            # Optionally, log the full text that caused the error
            # print(f"Problematic text: {comment.content}")

    if pain_points_to_save:
        save_pain_points(pain_points_to_save)
        print(f"[bold green]Successfully detected and saved {len(pain_points_to_save)} new pain points.[/bold green]")
    else:
        print("[bold yellow]No new pain points detected.[/bold yellow]")


@app.command()
def pain_points(
    advanced: bool = typer.Option(False, "--advanced", help="Use the advanced transformer-based NLP model for higher accuracy.")
):
    """
    Run the pain point detection and analysis pipeline.
    """
    print("[bold green]Starting NLP processing for pain points...[/bold green]")
    try:
        process_pain_points(use_advanced_detector=advanced)
        print("[bold green]Pain point processing completed successfully.[/bold green]")
    except Exception as e:
        print(f"[bold red]An error occurred during NLP processing: {e}[/bold red]")
        
if __name__ == "__main__":
    app() 