#!/usr/bin/env python3
"""
Export marimo apps from a folder into a repo subdirectory for GitHub Pages.
Usage:
  uv run .github/scripts/build_marimo.py \
      --apps-dir 04_marimo \
      --output-dir marimo \
      --template .github/scripts/index.tailwind.html.j2
"""

# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "jinja2==3.1.3",
#   "loguru==0.7.0",
#   "fire==0.7.0"
# ]
# ///

from pathlib import Path
from typing import List
import subprocess
import fire
import jinja2
from loguru import logger

def _export_one(app: Path, out_dir: Path) -> Path | None:
    out_file = out_dir / app.with_suffix(".html").name
    out_file.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "uvx", "marimo", "export", "html-wasm", "--sandbox",
        "--mode", "run", "--no-show-code",
        str(app), "-o", str(out_file),
    ]
    logger.debug(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True, text=True, capture_output=True)
        return out_file
    except subprocess.CalledProcessError as e:
        logger.error(f"Export failed for {app}:\n{e.stderr}")
        return None

def _render_index(items: List[dict], out_dir: Path, template_file: Path):
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_file.parent),
        autoescape=jinja2.select_autoescape(["html", "xml"]),
    )
    template = env.get_template(template_file.name)
    html = template.render(apps=items)
    (out_dir / "index.html").write_text(html, encoding="utf-8")
    logger.info(f"Wrote index: {out_dir / 'index.html'}")

def main(
    apps_dir: str = "04_marimo",
    output_dir: str = "marimo",
    template: str = ".github/scripts/index.tailwind.html.j2",
):
    apps_path = Path(apps_dir)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    if not apps_path.exists():
        logger.warning(f"No apps directory found: {apps_path}")
        return

    apps = sorted(p for p in apps_path.rglob("*.py"))
    if not apps:
        logger.warning(f"No marimo apps found under {apps_path}")
        return

    exported = []
    for app in apps:
        html = _export_one(app, out_path)
        if html:
            exported.append({
                "name": app.stem.replace("_", " ").title(),
                "py_path": str(app),
                "html_path": str(html.relative_to(out_path)),  # relative link
            })

    if not exported:
        logger.warning("No apps exported; skipping index generation.")
        return

    _render_index(exported, out_path, Path(template))
    logger.info(f"Exported {len(exported)} marimo apps to {out_path}")

if __name__ == "__main__":
    fire.Fire(main)
