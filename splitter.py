import logging
from logging.handlers import RotatingFileHandler
from logging import handlers
import sys


from pathlib import Path
import typer

from documents import Document
from output_writer import OutputWriter
from prompt import Prompt

log = logging.getLogger(__name__)


app = typer.Typer()

DEFAULT_MAX_WORDS = 1000

@app.command()
def create_parts(
    file_path: str = typer.Argument(
        ..., help="Path to the file to split into parts"
    ),
    max_words: int = typer.Option(
        DEFAULT_MAX_WORDS, help="Maximum number of words per part", show_default=True
    ),
):
    """Create parts of a file with a maximum number of words."""
    log.info(f"Starting process for file: {file_path}")

    file_path = Path(file_path)

    # Create prompt
    prompt = Prompt("prompt.txt")

    document = Document.from_file(file_path)

    # Split document into parts
    parts = document.split_into_parts(max_words)

    # Create output file
    output_file = file_path.parent / Path(file_path.stem + "_parts.txt")
    writer = OutputWriter(output_file, prompt)
    writer.write_parts(parts)

    log.info(f"Parts created in file: {output_file}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app() 
