"""
Build GitHub Pages site:
- Homepage from README.md (GFM) to _site/index.html
- Marimo notebooks from 04_marimo/*.py to _site/marimo/*.html
  and clean-URL copies at _site/marimo/<name>/index.html
- Create _site/.nojekyll and a simple marimo index
Usage:
    uv run .github/scripts/build.py
"""

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "fire==0.7.0",
#     "loguru==0.7.0"
# ]
# ///

import html
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable, List, Tuple

import fire
from loguru import logger

ROOT = Path.cwd()
SITE = ROOT / "_site"
MARIMO_SRC = ROOT / "04_marimo"
MARIMO_OUT = SITE / "marimo"


def run(cmd: List[str]) -> None:
    logger.debug("Running: {}", " ".join(cmd))
    subprocess.run(cmd, check=True)


def build_homepage(readme: Path = ROOT / "README.md", out: Path = SITE / "index.html") -> None:
    out.parent.mkdir(parents=True, exist_ok=True)

    css_url = "https://cdn.jsdelivr.net/npm/github-markdown-css/github-markdown.min.css"
    favicon_href = "/favicon.png"
    extra_head = (
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<link rel="icon" href="{favicon_href}" type="image/x-icon">'
        "<style>"
        "body { background:#0e1116; }"
        ".page { max-width: 1210px; margin: 2rem auto; padding: 2rem; background:#fff;"
        "box-shadow: 0 2px 18px rgba(0,0,0,.1); border-radius: 12px; }"
        ".markdown-body { box-sizing: border-box; min-width: 200px; }"
        "</style>"
    )

    logger.info("Building homepage from {}", readme)
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as headf:
        headf.write(extra_head)
        headf.flush()
        head_path = headf.name

    cmd = [
        "pandoc",
        "-f", "gfm",
        "-t", "html5",
        "-s", str(readme),
        "-o", str(out),
        "--metadata",
        "--css", css_url,
        "-V", "pagetitle=Starter Code — Open Data Basel-Stadt",
        "--include-in-header", head_path,   # <- use temp file instead of "-"
    ]
    try:
        run(cmd)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"pandoc failed with exit code {e.returncode}") from e

    # Wrap body content in a container for nicer look
    html_text = out.read_text(encoding="utf-8")
    html_text = html_text.replace("<body>", '<body><div class="page markdown-body">', 1)
    html_text = html_text.replace("</body>", "</div></body>", 1)
    out.write_text(html_text, encoding="utf-8")
    logger.success("Homepage → {}", out)


def export_marimo(py_path: Path, out_dir: Path) -> Tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_html = out_dir / f"{py_path.stem}.html"
    cmd = [
        "uvx", "marimo", "export", "html-wasm",
        "--sandbox",
        "--mode", "edit",
        str(py_path),
        "-o", str(out_html),
    ]
    run(cmd)
    logger.info("Exported marimo {} → {}", py_path.name, out_html.name)

    # Clean URL: marimo/<name>/index.html
    clean_dir = out_dir / py_path.stem
    clean_dir.mkdir(parents=True, exist_ok=True)
    clean_index = clean_dir / "index.html"
    shutil.copyfile(out_html, clean_index)
    logger.info("Clean URL ready at {}", clean_index)

    return out_html, clean_index


def list_marimo_apps(src_dir: Path) -> Iterable[Path]:
    return sorted(p for p in src_dir.glob("*.py") if p.is_file())


def build_marimo_index(out_dir: Path, apps: List[Path]) -> None:
    index = out_dir / "index.html"
    items = []
    for p in apps:
        name = p.stem
        items.append(
            f'<li><a href="./{html.escape(name)}/">{html.escape(name)}</a> '
            f'(<a href="./{html.escape(name)}.html">.html</a>)</li>'
        )
    html_doc = f"""<!doctype html>
<html lang="en"><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>marimo apps</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/github-markdown-css/github-markdown.min.css">
<style>
body {{ background:#ffffff; }}
.page {{ max-width: 1210px; margin: 2rem auto; padding: 2rem; background:#fff;
         box-shadow: 0 2px 18px rgba(0,0,0,.1); border-radius: 12px; }}
</style>
<body>
  <div class="page markdown-body">
    <h1>marimo apps</h1>
    <ul>
      {''.join(items) if items else '<li><em>No apps found.</em></li>'}
    </ul>
    <p><a href="../">← Back to Home</a></p>
  </div>
</body>
</html>"""
    index.write_text(html_doc, encoding="utf-8")
    logger.success("marimo index → {}", index)


def touch_nojekyll(root: Path = SITE) -> None:
    (root / ".nojekyll").write_text("", encoding="utf-8")
    logger.info("Wrote {}", root / ".nojekyll")


def main(
    source: str = str(MARIMO_SRC),
    output: str = str(SITE),
    marimo_out: str = str(MARIMO_OUT),
    readme: str = str(ROOT / "README.md"),
):
    SITE.mkdir(parents=True, exist_ok=True)
    src_fav = ROOT / "favicon.png"
    if src_fav.exists():
        shutil.copyfile(src_fav, SITE / "favicon.png")
    touch_nojekyll(SITE)
    build_homepage(Path(readme), SITE / "index.html")

    src_dir = Path(source)
    out_dir = Path(marimo_out)
    if not src_dir.exists():
        logger.warning("Marimo source folder not found: {}", src_dir)
        return

    apps = list(list_marimo_apps(src_dir))
    exported: List[Path] = []
    for app in apps:
        try:
            html_path, _ = export_marimo(app, out_dir)
            exported.append(html_path)
        except subprocess.CalledProcessError as e:
            logger.error("Export failed for {}:\n{}", app.name, e)
    build_marimo_index(out_dir, apps)
    logger.success("Build complete. Exported {}/{} marimo apps.", len(exported), len(apps))


if __name__ == "__main__":
    fire.Fire(main)
