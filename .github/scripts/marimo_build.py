"""
Export marimo notebooks from a folder to HTML/WASM (edit mode) into an output dir.

Usage:
    uv run .github/scripts/marimo_build.py --source 04_marimo --output-dir _site
"""

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "fire==0.7.0",
#     "loguru==0.7.0"
# ]
# ///

import subprocess
from pathlib import Path
from typing import Union
import fire
from loguru import logger


def _export_html_wasm(py_path: Path, out_dir: Path) -> bool:
    """Export one marimo .py to HTML/WASM in EDIT mode."""
    rel_html = py_path.with_suffix(".html").name  # just filename.html
    out_html = out_dir / rel_html
    out_html.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "uvx",
        "marimo",
        "export",
        "html-wasm",
        "--sandbox",
        "--mode",
        "edit",  # EDIT mode
        str(py_path),
        "-o",
        str(out_html),
    ]
    logger.debug(f"Running: {cmd}")
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Exported {py_path} -> {out_html}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Export failed for {py_path}\nSTDERR:\n{e.stderr}")
        return False


def main(source: Union[str, Path] = "04_marimo", output_dir: Union[str, Path] = "_site"):
    source_dir = Path(source)
    out_dir = Path(output_dir)

    logger.info(f"Source dir: {source_dir}")
    logger.info(f"Output dir: {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)

    py_files = sorted(source_dir.glob("*.py"))
    if not py_files:
        logger.warning("No marimo .py files found")
        return

    for nb in py_files:
        _export_html_wasm(nb, out_dir)

    logger.info("Build complete.")


if __name__ == "
