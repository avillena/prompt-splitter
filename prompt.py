from typing import Optional
import logging
from pathlib import Path


log = logging.getLogger(__name__)

class Prompt:
    def __init__(self, filepath: Path):
        self.text = ""
        try:
            with open(str(filepath), "r", encoding="utf-8") as file:
                self.text = file.read()
                log.info("Prompt " + self.text)

        except FileNotFoundError:
            log.info("No prompt file found.")

    def __str__(self) -> str:
        return self.text
