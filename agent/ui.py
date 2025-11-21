from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.text import Text

console = Console()


def render_tasks_table(tasks: List[Dict]):
    """Render a checklist-style table inspired by the sample UI image."""
    table = Table(show_header=False, box=None, expand=True)
    table.add_column("status", width=3)
    table.add_column("title")
    table.add_column("desc")

    status_symbol = {
        'not-started': '○',
        'in-progress': '◔',
        'done': '●',
        'failed': '✖',
        'needs-follow-up': '◐'
    }

    for t in tasks:
        s = t.get('status', 'not-started')
        sym = status_symbol.get(s, '○')
        title = Text(t.get('title', ''), style="bold")
        desc = Text(t.get('description', ''), style="dim")
        table.add_row(sym, title, desc)

    console.print(table)


def show_tasks_ui(tasks: List[Dict], generating: bool = False):
    """Simple blocking UI: show tasks in a To-dos panel and let the user choose to continue or edit.

    If `generating` is True, show a small generating indicator above the list.
    """
    console.clear()
    header = f"To-dos {len(tasks)}"
    if generating:
        header_text = Align.left(Text("Generating.", style="bold yellow"))
        console.print(header_text)

    console.print(Panel(Align.left(Text(header, style="bold white")), style="grey37"))
    render_tasks_table(tasks)

    console.print("\nOptions: [enter] continue  |  [e] edit  |  [q] quit")
    choice = input("Choice: ").strip().lower()
    return choice


def generate_landing_preview(output_path: str, site_title: str = "Coupon Bazaar"):
        """Create a simple static HTML preview for a landing page and write to output_path."""
        import os

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        html = f"""
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>{site_title} — Preview</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; margin:0; background:#0b0b0b; color:#e6eef8 }}
                .hero {{ padding:64px 24px; text-align:center; background:linear-gradient(90deg,#0f172a,#071023); }}
                .hero h1{{ font-size:36px; margin:0 0 12px }}
                .hero p{{ color:#9fb3d4; margin:0 0 20px }}
                nav {{ display:flex; gap:12px; justify-content:center; padding:12px }}
                .cards {{ display:flex; flex-wrap:wrap; gap:12px; padding:24px; justify-content:center }}
                .card {{ background:#071427; padding:16px; width:260px; border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.6) }}
                .card h3{{ margin:0 0 8px }}
                .cta {{ display:inline-block; margin-top:12px; padding:10px 14px; background:#0ea5a2; color:#022; border-radius:6px; text-decoration:none; font-weight:600 }}
            </style>
        </head>
        <body>
            <nav>
                <strong style="margin-right:16px">{site_title}</strong>
                <a href="#">Browse</a>
                <a href="#">Sell</a>
                <a href="#">About</a>
            </nav>
            <header class="hero">
                <h1>Save more on the things you love</h1>
                <p>Discover coupons, buy securely with escrow, and sell your own deals.</p>
                <a class="cta" href="#">Browse coupons</a>
            </header>
            <section class="cards">
                <div class="card">
                    <h3>50% off Coffee</h3>
                    <p>Local cafe — Expires 2026-01-01</p>
                </div>
                <div class="card">
                    <h3>25% off Gym</h3>
                    <p>Membership discount — Expires 2026-02-01</p>
                </div>
                <div class="card">
                    <h3>10% off Groceries</h3>
                    <p>Store promo — Expires 2026-03-01</p>
                </div>
            </section>
        </body>
        </html>
        """
        with open(output_path, "w", encoding="utf-8") as f:
                f.write(html)
        return output_path
