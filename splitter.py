import logging
from logging import handlers
import os
from pathlib import Path
import argparse

from documents import Document
from output_writer import OutputWriter
from prompt import Prompt

log = logging.getLogger(__name__)

DEFAULT_MAX_WORDS = 2046
DEFAULT_PROMPT_FILE = "prompt.txt"

def create_parts(file_path, max_tokens, force_paragraphs = False, prompt_filename = ""):
    """Create parts of a file with a maximum number of words."""
    log.info(f"Starting process for file: {file_path}")

    file_path = Path(file_path)

    # Create prompt
    if not prompt_filename:
        script_path = Path(os.path.realpath(os.path.dirname(__file__)))
        prompt = Prompt( script_path / "prompt.txt")
    else:
        prompt = Prompt( prompt_filename )

    document = Document.from_file(file_path)

    # Split document into parts
    parts = document.split_into_parts(max_tokens, force_paragraphs)

    # Create output file
    output_file = file_path.parent / Path(file_path.stem + "_parts.txt")
    writer = OutputWriter(output_file, prompt)
    writer.write_parts(parts)

    log.info(f"Parts created in file: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file_path', type=str, help="Path to the file to split into parts")
    parser.add_argument('--max-tokens', '-mt', type=int, default=DEFAULT_MAX_WORDS, help="Maximum number of words per part")
    parser.add_argument('--force-paragraphs','-fp', action='store_true', help="Force splitting at paragraph boundaries")
    parser.add_argument('--prompt', '-p', type=str, help="Path to the prompt file")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    create_parts(args.file_path, args.max_tokens, args.force_paragraphs, args.prompt)

