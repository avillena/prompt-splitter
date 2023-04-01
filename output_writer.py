from typing import List, Optional, TextIO
from prompt import Prompt


class OutputWriter:
    def __init__(self, file_path: str, prompt: Optional[Prompt] = None):
        self.file_path = file_path
        self.prompt = prompt

    def write_parts(self, parts: List[str]):
        with open(self.file_path, "w", encoding="utf-8") as file:
            for part_num, part_text in enumerate(parts, 1):
                file.write(f"{'#'*60}\nPART {part_num:03d}\n{'#'*60}\n\n")
                if self.prompt:
                    file.write(f"{self.prompt}\n\n")
                file.write(f"{part_text}\n\n")
